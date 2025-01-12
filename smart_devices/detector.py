import socket
import time
import random
import struct
import .device_pb2 as device_pb2  # Importando a definição do Protobuf
from .configs import *
def detect_presence():
    """Função para simular a detecção de presença."""
    # Simula a presença com base em um valor aleatório
    return random.choice(["entrando", "saindo", "nenhum"])

def send_presence_data(device_id, device_ip, device_port):
    """Envia os dados de presença para o gateway via multicast."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    group = socket.inet_aton(MCAST_GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Envia os dados do sensor de presença para o gateway
    while True:
        presence = detect_presence()

        # Criar a mensagem de descoberta com Protobuf
        discovery_message = device_pb2.DeviceDiscovery(
            device_id=device_id,
            device_ip=device_ip,
            device_port=device_port,
            device_type="sensor_presenca",  # Tipo do dispositivo
            state=presence  # Estado atual (entrando, saindo, nenhum)
        )

        # Serializar a mensagem
        message = discovery_message.SerializeToString()
        print(f"Enviando dados para o gateway: Sensor {device_id}, Presença: {presence}")
        
        # Envia via multicast
        sock.sendto(message, (MCAST_GROUP, MCAST_PORT))
        
        # Aguarda antes de enviar a próxima leitura de presença
        time.sleep(5)

def run_detector(device_id="sensor_presenca_1", device_ip=PRESENCE_SENSOR_IP, device_port=PRESENCE_SENSOR_PORT):
    send_presence_data(device_id, device_ip, device_port)

if __name__ == "__main__":
    run_detector()
