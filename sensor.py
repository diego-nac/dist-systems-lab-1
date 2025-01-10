import socket
import time
import random
import struct
import device_pb2  # Importando a definição do Protobuf

MCAST_GROUP = '224.0.0.1'  # Endereço multicast do gateway
MCAST_PORT = 5000          # Porta multicast do gateway

def get_temperature():
    """Função para simular a leitura da temperatura (em °C)."""
    # Simula uma temperatura aleatória entre 20 e 30 graus Celsius
    return round(random.uniform(20.0, 30.0), 2)

def send_temperature_data(device_id, device_ip, device_port):
    """Envia os dados de temperatura para o gateway via multicast."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    group = socket.inet_aton(MCAST_GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # Envia os dados do sensor de temperatura para o gateway
    while True:
        temperature = get_temperature()

        # Criar a mensagem de descoberta com Protobuf
        discovery_message = device_pb2.DeviceDiscovery(
            device_id=device_id,
            device_ip=device_ip,
            device_port=device_port,
            device_type="sensor",  # Tipo do dispositivo
            state="ativado",  # O sensor pode estar sempre "ativado"
            temperature=temperature
        )

        # Serializar a mensagem
        message = discovery_message.SerializeToString()
        print(f"Enviando dados para o gateway: Sensor {device_id}, Temperatura: {temperature}°C")
        
        # Envia via multicast
        sock.sendto(message, (MCAST_GROUP, MCAST_PORT))
        
        # Aguarda antes de enviar a próxima leitura de temperatura
        time.sleep(10)

def main():
    device_id = "sensor_1"
    device_ip = "192.168.0.11"  # IP do sensor de temperatura
    device_port = 6001  # Porta onde o sensor está enviando dados
    send_temperature_data(device_id, device_ip, device_port)

if __name__ == "__main__":
    main()
