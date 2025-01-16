import socket
import struct
import threading
import time
import smart_devices.proto.smart_devices_pb2 as proto  # Arquivo gerado a partir do Protobuf
from utils.configs import *  # Configurações compartilhadas

def parse_device_info(message, addr, discovered_ips, devices):
    """
    Desserializa e processa a mensagem de descoberta de dispositivos usando Protobuf.
    """
    try:
        # Deserializa a mensagem Protobuf
        device_data = proto.DeviceDiscovery()
        device_data.ParseFromString(message)

        device_id = device_data.device_id
        device_name = device_data.device_name
        device_type = device_data.device_type
        is_on = device_data.is_on
        brightness = device_data.brightness
        color = device_data.color
        device_ip = device_data.device_ip
        device_port = device_data.device_port

        # Atualiza informações do dispositivo no dicionário
        devices[device_id] = {
            'device_id': device_id,
            'device_name': device_name,
            'device_type': device_type,
            'is_on': is_on,
            'brightness': brightness,
            'color': color,
            'device_ip': device_ip,
            'device_port': device_port
        }

        # Log detalhado sobre o dispositivo descoberto
        if device_id not in discovered_ips:
            discovered_ips.add(device_id)
            print(f"Novo dispositivo descoberto:")
            print(f" - ID: {device_id}")
            print(f" - Nome: {device_name}")
            print(f" - Tipo: {device_type}")
            print(f" - Estado: {'ON' if is_on else 'OFF'}")
            if device_type.lower() == "lamp":
                print(f" - Brilho: {brightness * 100:.1f}%")
                print(f" - Cor: {color}")
            print(f" - IP: {device_ip}")
            print(f" - Porta: {device_port}")

    except Exception as e:
        print(f"Erro ao parsear a mensagem: {e}")

def multicast_receiver(devices, discovered_ips):
    """
    Escuta mensagens multicast enviadas pelos dispositivos.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', MCAST_PORT))

    group = socket.inet_aton(MCAST_GROUP) + socket.inet_aton(LOCAL_IP)
    try:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, group)
    except OSError as e:
        print(f"Erro ao configurar multicast: {e}")
        return

    print(f"Gateway aguardando mensagens de multicast em {MCAST_GROUP}:{MCAST_PORT}...")

    while True:
        try:
            data, addr = sock.recvfrom(BUFFER_SIZE)
            print(f"Mensagem recebida de {addr}")
            parse_device_info(data, addr, discovered_ips, devices)
        except Exception as e:
            print(f"Erro no recebimento de mensagem multicast: {e}")
def change_device_state(device_ip, device_port, command, device_id=None, brightness=None, color=None):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Conectando ao dispositivo {device_ip}:{device_port}")
            client_socket.connect((device_ip, device_port))

            device_command = proto.DeviceCommand()
            device_command.command = command
            if device_id:
                device_command.device_id = device_id
            if brightness is not None:
                device_command.brightness = brightness
            if color:
                device_command.color = color

            print(f"Enviando comando: {command}")
            client_socket.sendall(device_command.SerializeToString())

            response = client_socket.recv(1024)
            command_response = proto.CommandResponse()
            command_response.ParseFromString(response)

            print(f"Resposta do dispositivo: {command_response.message}")

    except Exception as e:
        print(f"Erro ao enviar comando para {device_ip}:{device_port}: {e}")


def client_listener(devices):
    """
    Escuta comandos de cliente (via TCP) para controlar dispositivos.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permite reutilizar o endereço
    server_socket.bind(('localhost', 7000))  # Vincula o socket ao IP e porta
    server_socket.listen(5)  # Define o número de conexões pendentes na fila
    print("Gateway aguardando comandos do cliente na porta 7000...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Conexão recebida de {client_address}")

        try:
            command_data = client_socket.recv(1024)
            if command_data:
                device_command = proto.DeviceCommand()
                device_command.ParseFromString(command_data)

                print(f"Comando recebido: {device_command.command}")
                response_message = handle_client_command(device_command, devices)
                command_response = proto.CommandResponse(success=True, message=response_message)
                client_socket.sendall(command_response.SerializeToString())
        except Exception as e:
            print(f"Erro ao processar comando do cliente: {e}")
        finally:
            client_socket.close()
def handle_client_command(command, devices):
    """
    Processa o comando do cliente e retorna a resposta.
    """
    if command.command.lower() == 'listar dispositivos':
        if not devices:
            return "Nenhum dispositivo conectado."
        
        return "\n".join([
            f"{dev_id}: {info.get('device_type', 'desconhecido')} em {info.get('device_ip', 'desconhecido')}:{info.get('device_port', 'desconhecido')}\n"
            f"  Estado: {'ON' if info.get('is_on', False) else 'OFF'}\n"
            f"  Brilho: {round(info.get('brightness', 'N/A')*100,2)}\n"
            f"  Cor: {info.get('color', 'N/A')}"
            for dev_id, info in devices.items()
        ])
    elif command.command.lower() == 'brightness':
        device_id = command.device_id
        if device_id in devices:
            device_info = devices[device_id]
            threading.Thread(
                target=change_device_state,
                args=(device_info['device_ip'], device_info['device_port'], 'brightness', device_id, command.brightness)
            ).start()
            return f"Comando de luminosidade enviado para {device_id}."
        else:
            return f"Dispositivo {device_id} não encontrado."

    elif command.command.lower() in ['ligar', 'desligar']:
        device_id = command.device_id
        if device_id in devices:
            device_info = devices[device_id]
            threading.Thread(
                target=change_device_state, 
                args=(device_info.get('device_ip'), device_info.get('device_port'), command.command)
            ).start()
            return f"Comando '{command.command}' enviado para {device_id}."
        else:
            return f"Dispositivo {device_id} não encontrado."
    
    elif command.command.lower() == 'alterar cor':
        device_id = command.device_id
        if device_id in devices:
            device_info = devices[device_id]
            threading.Thread(
                target=change_device_state, 
                args=(device_info.get('device_ip'), device_info.get('device_port'), 'alterar cor', device_id, None, command.color)
            ).start()
            return f"Comando de alteração de cor enviado para {device_id}."
        else:
            return f"Dispositivo {device_id} não encontrado."
    else:
        return f"Comando desconhecido: {command.command}"


def main():
    devices = {}
    discovered_ips = set()

    threading.Thread(target=multicast_receiver, args=(devices, discovered_ips), daemon=True).start()
    threading.Thread(target=client_listener, args=(devices,), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Gateway encerrado pelo usuário.")

if __name__ == "__main__":
    main()
