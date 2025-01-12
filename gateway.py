import socket
import struct
import threading
import time
from utils import *
# Função para parsear a informação do dispositivo a partir da mensagem multicast
def parse_device_info(message, addr, discovered_ips, devices):
    try:
        # Exemplo de mensagem: "Lamp(ID: 1, Name: Living Room Lamp, State: OFF, Brightness: 50%, Color: blue, IP: 239.0.0.2, Port: 1111)"
        parts = [part.strip() for part in message.split(',')]

        # Validação básica do formato da mensagem
        if len(parts) < 7:
            print(f"Mensagem inválida recebida: {message}")
            return

        # Extrai campos obrigatórios da mensagem
        device_id = parts[0].split(':')[1].strip()  # Ex.: "1"
        device_name = parts[1].split(':')[1].strip()  # Ex.: "Living Room Lamp"
        device_state = parts[2].split(':')[1].strip().upper()  # Ex.: "OFF"
        brightness_str = parts[3].split(':')[1].replace('%', '').strip()  # Ex.: "50"
        color = parts[4].split(':')[1].strip().lower()  # Ex.: "blue"
        device_ip = parts[5].split(':')[1].strip()  # Ex.: "239.0.0.2"

        # Corrige a extração da porta para remover caracteres extras
        device_port_str = parts[6].split(':')[1].strip()
        device_port = int(device_port_str.rstrip(')'))  # Remove o parêntese fechado

        # Converte e valida valores
        is_on = device_state == "ON"
        try:
            brightness = int(brightness_str)
            if not (0 <= brightness <= 100):
                raise ValueError(f"Brilho fora do intervalo: {brightness_str}")
        except ValueError:
            print(f"Erro ao parsear o brilho: {brightness_str}")
            return

        # Evita registrar o mesmo dispositivo múltiplas vezes
        if device_ip not in discovered_ips:
            print(f"Dispositivo {device_id} localizado em {device_ip}:{device_port}.")
            discovered_ips.add(device_ip)

        # Atualiza ou adiciona informações do dispositivo
        devices[device_id] = {
            'id': device_id,
            'name': device_name,
            'type': 'lamp',
            'state': is_on,
            'brightness': brightness,
            'color': color,
            'ip': device_ip,
            'port': device_port
        }
        print(f"Dispositivo {device_name} ({device_id}) atualizado com sucesso.")

    except Exception as e:
        print(f"Erro ao parsear a mensagem: {e}")




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
        message = data.decode('utf-8')
        print(f"Mensagem recebida de {addr}: {message}")

        
        parse_device_info(message, addr, discovered_ips, devices)


def change_device_state(device_ip, device_port, command):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((device_ip, device_port))
            print(f"Conectado ao dispositivo {device_ip}:{device_port}. Enviando comando: {command}")

            # Enviar comando para o dispositivo
            client_socket.sendall(command.encode())

            # Receber a resposta do dispositivo
            response = client_socket.recv(1024)
            print(f"Resposta do dispositivo: {response.decode()}")
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
        command = client_socket.recv(1024).decode()
        if command:
            print(f"Comando recebido do cliente: {command}")
        # Dividir o comando para obter o ID do dispositivo e o comando (ligar, desligar, luminosidade, listar dispositivos)
        command_parts = command.split()

        if command_parts[0].lower() == 'listar' and command_parts[1].lower() == 'dispositivos':
            # Comando para listar dispositivos
            if devices:
                device_list = ""
                for device_id, device_info in devices.items():
                    if device_info['type'] == 'lamp':
                        device_list += f"{device_id}: {device_info['ip']}:{device_info['port']} (Lâmpada) - Luminosidade: {device_info['luminosity']}%\n"
                    elif device_info['type'] == 'sensor':
                        device_list += f"{device_id}: {device_info['ip']}:{device_info['port']} (Sensor de Temperatura) - Temperatura: {device_info['temperature']}\n"
                client_socket.sendall(f"Dispositivos encontrados:\n{device_list}".encode())
            else:
                client_socket.sendall("Nenhum dispositivo encontrado.".encode())

        # Comando para ligar ou desligar dispositivos
        elif len(command_parts) == 2:
            action = command_parts[0]
            device_id = command_parts[1]

            # Verificar se o dispositivo existe
            if device_id in devices:
                device_ip, device_port = devices[device_id]['ip'], devices[device_id]['port']
                threading.Thread(target=change_device_state, args=(device_ip, device_port, action)).start()
                # Enviar resposta ao cliente
                client_socket.sendall(f"Comando '{action}' para o dispositivo {device_id} foi executado.".encode())
            else:
                client_socket.sendall(f"Dispositivo {device_id} não encontrado.".encode())

        # Comando para ajustar a luminosidade
        elif len(command_parts) == 3 and command_parts[0] == 'luminosidade':
            
            device_id = command_parts[1]
            try:
                luminosity_value = int(command_parts[2])
                if 0 <= luminosity_value <= 100:
                    if device_id in devices:
                        devices[device_id]['luminosity'] = luminosity_value  # Atualiza a luminosidade do dispositivo
                        # Enviar comando para a lâmpada ajustar a luminosidade
                        device_ip = devices[device_id]['ip']
                        device_port = devices[device_id]['port']
                        command = f"luminosidade {luminosity_value}"
                        threading.Thread(target=change_device_state, args=(device_ip, device_port, command)).start()
                        client_socket.sendall(f"Luminosidade da lâmpada {device_id} ajustada para {luminosity_value}%.".encode())
                    else:
                        client_socket.sendall(f"Dispositivo {device_id} não encontrado.".encode())
                else:
                    client_socket.sendall("Valor de luminosidade inválido. Use um valor entre 0 e 100.".encode())
            except ValueError:
                client_socket.sendall("Comando luminosidade inválido. Use: 'luminosidade <id> <valor entre 0 e 100>'.".encode())
        # Caso o comando seja inválido
        else:
            client_socket.sendall("Comando inválido. Use: 'ligar <ID>' ou 'desligar <ID>' ou 'luminosidade <ID> <valor entre 0 e 100>'.".encode())

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
