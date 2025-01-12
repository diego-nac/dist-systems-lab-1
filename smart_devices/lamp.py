import socket
import struct
import threading
import time
import random
import device_pb2 as device_pb2
from configs import *

DEVICE_TYPE = 'lamp'
DEVICE_STATE = 'desligada'
LUMINOSITY = 0

# Funções auxiliares
def generate_device_id():
    return f"lampada{random.randint(1000, 9999)}"

def generate_device_ip():
    return f"127.0.1.{random.randint(0, 255)}"

def send_discovery(device_id, device_ip, device_port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        discovery_message = device_pb2.DeviceDiscovery(
            device_id=device_id,
            device_ip=device_ip,
            device_port=device_port,
            device_type=DEVICE_TYPE,
            state=DEVICE_STATE,
            luminosity=LUMINOSITY
        )
        message = discovery_message.SerializeToString()
        sock.sendto(message, (MCAST_GROUP, MCAST_PORT))
        sock.close()
    except Exception as e:
        print(f"Erro ao enviar mensagem de descoberta: {e}")

def listen_for_commands(device_ip, device_port):
    global DEVICE_STATE, LUMINOSITY
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', device_port))
    server_socket.listen(5)

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            data = client_socket.recv(1024)
            if data:
                device_command = device_pb2.DeviceCommand()
                device_command.ParseFromString(data)

                command_response = device_pb2.CommandResponse()
                if device_command.command == "ligar":
                    DEVICE_STATE = "ligada"
                    LUMINOSITY = 100
                    command_response.message = "Lâmpada ligada."
                elif device_command.command == "desligar":
                    DEVICE_STATE = "desligada"
                    LUMINOSITY = 0
                    command_response.message = "Lâmpada desligada."
                elif device_command.command == "luminosidade":
                    luminosity_level = device_command.luminosity
                    if 0 <= luminosity_level <= 100:
                        LUMINOSITY = luminosity_level
                        command_response.message = f"Luminosidade ajustada para {LUMINOSITY}%."
                        if luminosity_level != 0:
                            DEVICE_STATE = "ligada"
                    else:
                        command_response.message = "Valor de luminosidade inválido."
                else:
                    command_response.message = "Comando inválido."

                response_data = command_response.SerializeToString()
                client_socket.sendall(response_data)

            client_socket.close()
        except socket.error as e:
            print(f"Erro de socket: {e}")
        except Exception as e:
            print(f"Erro ao processar comando: {e}")

def start_lamp(device_id, device_ip, device_port):
    while True:
        send_discovery(device_id, device_ip, device_port)
        time.sleep(DELAY_DISCOVERY)

def run_lamp(device_id = 'lamp_1', device_ip = LAMP_IP, device_port = LAMP_PORT):
    threading.Thread(target=start_lamp, args=(device_id, device_ip, device_port), daemon=True).start()
    threading.Thread(target=listen_for_commands, args=(device_ip,device_port), daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nLâmpada desligada.")

if __name__ == "__main__":
    run_lamp()
