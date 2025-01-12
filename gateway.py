import socket
import struct
import threading
import time
import smart_devices.device_pb2 as device_pb2  # Importando o arquivo gerado a partir do device.proto

MCAST_GROUP = '224.0.0.1'  # Endereço multicast
MCAST_PORT = 5000          # Porta multicast
BUFFER_SIZE = 1024         # Tamanho do buffer para leitura de mensagens
# Função para parsear a informação do dispositivo a partir da mensagem multicast
def parse_device_info(message, addr, discovered_ips, devices):
    try:
        # Deserializa a mensagem Protobuf
        device_data = device_pb2.DeviceDiscovery()
        device_data.ParseFromString(message)

        device_id = device_data.device_id
        device_ip = device_data.device_ip
        device_port = device_data.device_port
        device_type = device_data.device_type
        state = device_data.state

        if device_type == "sensor":
            # Exibe a temperatura recebida
            temperature = round(device_data.temperature, 2)
            print(f"Temperatura recebida de {device_id} ({device_ip}:{device_port}): {temperature}°C")
            devices[device_id] = {'ip': device_ip, 'port': device_port, 'type': 'sensor', 'temperature': temperature}
        
        elif device_type == "lampada":
            # Lógica para dispositivos de lâmpada
            luminosity = device_data.luminosity
            print(f'Dispositivo {device_id} ({device_ip}:{device_port}) Estado: {state} Luminosidade: {luminosity}')
            devices[device_id] = {'ip': device_ip, 'port': device_port, 'type': 'lamp', 'luminosity': luminosity}

        elif device_type == "sensor_presenca":
            # Lógica para dispositivos de sensor de presença
            print(f'Sensor de presença {device_id} ({device_ip}:{device_port}) Estado: {state}')
            devices[device_id] = {'ip': device_ip, 'port': device_port, 'type': 'sensor_presenca', 'state': state}

        if device_ip not in discovered_ips:
            print(f"Dispositivo {device_id} localizado em {device_ip}:{device_port}.")
            discovered_ips.add(device_ip)

    except Exception as e:
        print(f"Erro ao parsear a mensagem: {e}")

# Função para escutar as mensagens de multicast
def multicast_receiver(devices, discovered_ips):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', MCAST_PORT))

    group = socket.inet_aton(MCAST_GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    print(f"Gateway aguardando mensagens de multicast em {MCAST_GROUP}:{MCAST_PORT}...")

    while True:
        data, addr = sock.recvfrom(BUFFER_SIZE)
        print(f"Mensagem recebida de {addr}")
        parse_device_info(data, addr, discovered_ips, devices)

# Função para enviar comandos de controle para o dispositivo via TCP usando Protobuf
def change_device_state(device_ip, device_port, command, lamp_id=None, luminosity=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((device_ip, device_port))
            print(f"Conectado ao dispositivo {device_ip}:{device_port}. Enviando comando: {command}")
            

            # Criar a mensagem de comando com Protobuf
            device_command = device_pb2.DeviceCommand()
            device_command.command = command
            if lamp_id is not None:
                device_command.device_id = lamp_id
            if luminosity is not None:
                device_command.luminosity = luminosity

            # Serializar a mensagem de comando
            message = device_command.SerializeToString()

            # Enviar comando para o dispositivo
            client_socket.sendall(message)

            # Receber a resposta do dispositivo
            response = client_socket.recv(1024)
            command_response = device_pb2.CommandResponse()
            command_response.ParseFromString(response)

            print(f"Resposta do dispositivo: {command_response.message}")

    except (socket.timeout, socket.error) as e:
        print(f"Erro ao conectar no dispositivo {device_ip}:{device_port}. Erro: {e}")


# Função para escutar comandos do cliente (via TCP) para controlar dispositivos
def client_listener(devices):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 7000))  # Porta do servidor TCP do gateway para escutar comandos do cliente
    server_socket.listen(5)
    print("Gateway aguardando comandos do cliente na porta 7000...")
    
    while True:
        client_socket, client_address = server_socket.accept()
        
        print(f"Conexão recebida de {client_address}")

        # Receber o comando do cliente
        command_data = client_socket.recv(1024)  # Recebe o comando em formato binário Protobuf

        if command_data:
            try:
                # Deserializa a mensagem do comando do cliente (Protobuf)
                device_command = device_pb2.DeviceCommand()
                device_command.ParseFromString(command_data)

                print(f"Comando recebido: {device_command.command}")

                # Cria o objeto de resposta CommandResponse
                command_response = device_pb2.CommandResponse()

                # Processa o comando e prepara a resposta
                if device_command.command.lower() == 'listar dispositivos':
                    # Comando para listar dispositivos
                    if devices:
                        device_list = ""
                        for device_id, device_info in devices.items():
                            if device_info['type'] == 'lamp':
                                device_list += f"{device_id}: {device_info['ip']}:{device_info['port']} (Lâmpada) - Luminosidade: {device_info['luminosity']}%\n"
                            elif device_info['type'] == 'sensor':
                                device_list += f"{device_id}: {device_info['ip']}:{device_info['port']} (Sensor de Temperatura) - Temperatura: {device_info['temperature']}°C\n"
                            elif device_info['type'] == 'sensor_presenca':
                                device_list += f"{device_id}: {device_info['ip']}:{device_info['port']} (Sensor de Presença) - Estado: {device_info['state']}\n"

                        command_response.success = True
                        command_response.message = f"Dispositivos encontrados:\n{device_list}"

                        
                        
                    else:
                        command_response.success = False
                        command_response.message = "Nenhum dispositivo encontrado."

                elif device_command.command.lower() == 'ligar' or device_command.command.lower() == 'desligar':
                    # Comando para ligar ou desligar o dispositivo
                    device_id = device_command.device_id
                    if device_id in devices:
                        device_ip, device_port = devices[device_id]['ip'], devices[device_id]['port']
                        threading.Thread(target=change_device_state, args=(device_ip, device_port, device_command.command)).start()
                        command_response.success = True
                        command_response.message = f"Comando '{device_command.command}' para o dispositivo {device_id} foi executado."
                    else:
                        command_response.success = False
                        command_response.message = f"Dispositivo {device_id} não encontrado."

                elif device_command.command.lower() == 'luminosidade':
                    # Comando para ajustar a luminosidade
                    if 0 <= device_command.luminosity <= 100:
                        device_id = device_command.device_id
                        if device_id in devices:
                            devices[device_id]['luminosity'] = device_command.luminosity  # Atualiza a luminosidade do dispositivo
                            device_ip = devices[device_id]['ip']
                            device_port = devices[device_id]['port']
                            threading.Thread(target=change_device_state, args=(device_ip, device_port, "luminosidade", device_id ,device_command.luminosity )).start()
                            command_response.success = True
                            command_response.message = f"Luminosidade da lâmpada {device_id} ajustada para {device_command.luminosity}%."
                        else:
                            command_response.success = False
                            command_response.message = f"Dispositivo {device_id} não encontrado."
                    else:
                        command_response.success = False
                        command_response.message = "Valor de luminosidade inválido. Use um valor entre 0 e 100."
                
                # Envia a resposta para o cliente
                client_socket.sendall(command_response.SerializeToString())

            except Exception as e:
                command_response.success = False
                command_response.message = f"Erro ao processar comando: {e}"
                client_socket.sendall(command_response.SerializeToString())

        client_socket.close()

# Função principal que inicia o multicast, aguarda comandos do cliente e controla os dispositivos
def main():
    devices = {}  # Dicionário para armazenar os dispositivos descobertos
    discovered_ips = set()  # Conjunto para armazenar IPs de dispositivos já descobertos

    # Criar uma thread para escutar o multicast sem bloquear a execução principal
    threading.Thread(target=multicast_receiver, args=(devices, discovered_ips), daemon=True).start()

    # Iniciar o escutador de comandos TCP do cliente
    threading.Thread(target=client_listener, args=(devices,), daemon=True).start()

    # O gateway continua rodando e pode processar comandos recebidos
    try:
        while True:
            time.sleep(1)  # O gateway continua funcionando
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")

if __name__ == "__main__":
    main()
