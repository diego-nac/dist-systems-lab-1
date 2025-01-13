import socket
import struct
import threading
import time
import smart_devices.proto.smart_devices_pb2 as device_pb2
from utils import *

class Gateway:
    def __init__(self, tcp_host='localhost', tcp_port=7000):
        """
        Inicializa o gateway, que gerencia dispositivos descobertos e comandos de cliente.
        
        :param tcp_host: Host/IP no qual o gateway escuta comandos via TCP.
        :param tcp_port: Porta na qual o gateway escuta comandos via TCP.
        """
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        
        # Dicionário para armazenar informações dos dispositivos descobertos
        # Ex: devices[device_id] = {
        #       'ip': <str>,
        #       'port': <int>,
        #       'type': <str>,
        #       'luminosity': <int> ou 'temperature': <float>, etc.
        #    }
        self.devices = {}
        
        # Conjunto para armazenar IPs já descobertos (evitar repetição de logs)
        self.discovered_ips = set()

    def parse_device_info(self, message, addr):
        """
        Desserializa e processa a mensagem multicast de descoberta do dispositivo.
        """
        try:
            device_data = device_pb2.DeviceDiscovery()
            device_data.ParseFromString(message)

            device_id   = device_data.device_id
            device_ip   = device_data.device_ip
            device_port = device_data.device_port
            device_type = device_data.device_type
            is_on       = device_data.is_on

            # Lógica de armazenamento (exemplos de campos específicos):
            if device_type.lower() == "sensor":
                temperature = round(device_data.brightness, 2)  # Exemplo: se brightness fosse algo como "temperatura"
                logger.info(f"Sensor de temperatura {device_id} => {temperature}°C")
                self.devices[device_id] = {
                    'ip': device_ip,
                    'port': device_port,
                    'type': 'sensor',
                    'temperature': temperature
                }

            elif device_type.lower() == "lamp" or device_type.lower() == "lampada":
                luminosity = round(device_data.brightness, 2)
                logger.info(f"Lâmpada {device_id} => Estado: {'ON' if is_on else 'OFF'} | Luminosidade: {luminosity}%")
                self.devices[device_id] = {
                    'ip': device_ip,
                    'port': device_port,
                    'type': 'lamp',
                    'luminosity': luminosity,
                    'state': 'ligada' if is_on else 'desligada'
                }

            else:
                logger.info(f"Dispositivo {device_id} do tipo '{device_type}' descoberto.")
                # Armazena genericamente
                self.devices[device_id] = {
                    'ip': device_ip,
                    'port': device_port,
                    'type': device_type,
                    'is_on': is_on
                }

            # Log de descoberta
            if device_ip not in self.discovered_ips:
                logger.info(f"Dispositivo {device_id} localizado em {device_ip}:{device_port}")
                self.discovered_ips.add(device_ip)

        except Exception as e:
            logger.info(f"Erro ao parsear a mensagem: {e}")

    def multicast_receiver(self):
        """
        Escuta as mensagens de multicast enviadas pelos dispositivos.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', MCAST_PORT))

        group = socket.inet_aton(MCAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        logger.info(f"Aguardando mensagens de multicast em {MCAST_GROUP}:{MCAST_PORT}...")

        while True:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            logger.info(f"Mensagem recebida de {addr}")
            self.parse_device_info(data, addr)

    def change_device_state(self, device_ip, device_port, command, lamp_id=None, luminosity=None):
        """
        Envia um comando TCP (Protobuf) a um dispositivo para mudar estado ou ajustar luminosidade.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((device_ip, device_port))
                logger.info(f"Conectado ao dispositivo {device_ip}:{device_port}. Comando: {command}")

                # Monta a mensagem Protobuf
                device_command = device_pb2.DeviceCommand()
                device_command.command = command
                if lamp_id:
                    device_command.device_id = lamp_id
                if luminosity is not None:
                    device_command.brightness = float(luminosity)

                # Serializa e envia
                message = device_command.SerializeToString()
                client_socket.sendall(message)

                # Recebe resposta
                response = client_socket.recv(1024)
                command_response = device_pb2.CommandResponse()
                command_response.ParseFromString(response)
                logger.info(f"Resposta do dispositivo: {command_response.message}")

        except (socket.timeout, socket.error) as e:
            logger.info(f"Erro ao conectar {device_ip}:{device_port}. Erro: {e}")

    def client_listener(self):
        """
        Escuta comandos de cliente (via TCP) e processa-os para controlar os dispositivos.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.tcp_host, self.tcp_port))
        server_socket.listen(5)
        logger.info(f"Aguardando comandos do cliente em {self.tcp_host}:{self.tcp_port}...")

        while True:
            client_socket, client_address = server_socket.accept()
            logger.info(f"Conexão recebida de {client_address}")

            data = client_socket.recv(1024)
            if data:
                try:
                    device_command = device_pb2.DeviceCommand()
                    device_command.ParseFromString(data)

                    logger.info(f"Comando recebido do cliente: {device_command.command}")

                    command_response = device_pb2.CommandResponse(success=False, message="")

                    if device_command.command.lower() == 'listar dispositivos':
                        if self.devices:
                            lista = ""
                            for dev_id, dev_info in self.devices.items():
                                tipo = dev_info.get('type', 'desconhecido')
                                lista += f"{dev_id} => Tipo: {tipo} | IP: {dev_info['ip']}:{dev_info['port']}\n"
                            command_response.success = True
                            command_response.message = f"Dispositivos:\n{lista}"
                        else:
                            command_response.message = "Nenhum dispositivo encontrado."

                    elif device_command.command.lower() in ['ligar', 'desligar']:
                        # Liga ou desliga a lâmpada
                        dev_id = device_command.device_id
                        if dev_id in self.devices:
                            dev_ip = self.devices[dev_id]['ip']
                            dev_port = self.devices[dev_id]['port']
                            # dispara thread para envio do comando
                            threading.Thread(
                                target=self.change_device_state,
                                args=(dev_ip, dev_port, device_command.command, dev_id)
                            ).start()
                            command_response.success = True
                            command_response.message = f"Comando '{device_command.command}' enviado para {dev_id}"
                        else:
                            command_response.message = f"Dispositivo '{dev_id}' não encontrado."

                    elif device_command.command.lower() == 'luminosidade':
                        dev_id = device_command.device_id
                        luminosity_value = device_command.brightness
                        if dev_id in self.devices:
                            if 0 <= luminosity_value <= 100:
                                dev_ip = self.devices[dev_id]['ip']
                                dev_port = self.devices[dev_id]['port']
                                # Atualiza local e manda o comando
                                self.devices[dev_id]['luminosity'] = luminosity_value
                                threading.Thread(
                                    target=self.change_device_state,
                                    args=(dev_ip, dev_port, "luminosidade", dev_id, luminosity_value)
                                ).start()
                                command_response.success = True
                                command_response.message = f"Luminosidade de {dev_id} ajustada para {luminosity_value}%."
                            else:
                                command_response.message = f"Valor de luminosidade inválido. Use 0 a 100."
                        else:
                            command_response.message = f"Dispositivo '{dev_id}' não encontrado."

                    else:
                        command_response.message = f"Comando '{device_command.command}' não suportado."

                    # Envia a resposta de volta ao cliente
                    client_socket.sendall(command_response.SerializeToString())

                except Exception as e:
                    logger.info(f"Erro ao processar comando: {e}")
                    # Resposta de erro
                    command_response = device_pb2.CommandResponse(success=False, message=f"Erro: {e}")
                    client_socket.sendall(command_response.SerializeToString())

            client_socket.close()

    def start(self):
        """
        Inicia o gateway, criando threads para:
          - Receber mensagens multicast dos dispositivos
          - Escutar por comandos de clientes
        """
        # Thread do multicast
        threading.Thread(target=self.multicast_receiver, daemon=True).start()
        # Thread do socket TCP para escutar comandos do cliente
        threading.Thread(target=self.client_listener, daemon=True).start()

        logger.info("Gateway iniciado. Recebendo dispositivos e aguardando comandos...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário.")

# Exemplo de uso
if __name__ == "__main__":
    gateway = Gateway(tcp_host="localhost", tcp_port=7000)
    gateway.start()
