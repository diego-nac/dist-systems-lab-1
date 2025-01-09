import socket
import struct
import threading
import time

# Parâmetros de configuração do grupo de multicast
MCAST_GROUP = '224.0.0.1'  # Endereço multicast
MCAST_PORT = 5000          # Porta multicast
BUFFER_SIZE = 1024         # Tamanho do buffer para leitura de mensagens

# Função para parsear a informação do dispositivo a partir da mensagem multicast
def parse_device_info(message, addr, discovered_ips, devices):
    try:
        # Exemplo de mensagem: "Dispositivo lampada123 foi descoberto, IP: 192.168.0.10, Porta: 6000"
        parts = message.split(',')
        device_id = parts[0].split(' ')[1]  # Obtém o ID do dispositivo
        device_ip = parts[1].split(':')[1].strip()  # Obtém o IP do dispositivo
        device_port = int(parts[2].split(':')[1].strip())  # Obtém a porta do dispositivo

        # Agora, utilizamos o IP e porta do remetente (no 'addr') como a origem da descoberta
        sender_ip = addr[0]  # IP de quem enviou a mensagem (endereço do multicast)
        sender_port = addr[1]  # Porta de quem enviou a mensagem

        if "Sensor" in message:
            # Exibe a temperatura recebida
            temperature = parts[3].split(':')[1].strip()
            print(f"Temperatura recebida de {device_id} ({device_ip}:{device_port}): {temperature}°C")
            devices[device_id] = {'ip': device_ip, 'port': device_port, 'type': 'sensor', 'temperature': temperature}
        elif "Dispositivo" in message:
            # Lógica para dispositivos de lâmpada
            luminosity = parts[4].split(':')[1].strip()
            if device_ip not in discovered_ips:
                print(f"Dispositivo {device_id} localizado em {device_ip}:{device_port}.")
                discovered_ips.add(device_ip)
            devices[device_id] = {'ip': device_ip, 'port': device_port, 'type': 'lamp', 'luminosity': luminosity}


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
        message = data.decode('utf-8')
        print(f"Mensagem recebida de {addr}: {message}")

        # Aqui, o gateway descobre o dispositivo e armazena informações (IP, Porta, ID)
        parse_device_info(message, addr, discovered_ips, devices)

# Função para enviar comandos de controle para o dispositivo via TCP
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
