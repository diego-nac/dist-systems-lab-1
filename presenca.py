import socket
import time
import cv2
import random
import struct
import device_pb2

MCAST_GROUP = '224.0.0.1'  # Endereço multicast do gateway
MCAST_PORT = 5000          # Porta multicast do gateway

class PresencaSensor:
    def __init__(self, device_id, device_ip, device_port):
        self.device_id = device_id
        self.device_ip = device_ip
        self.device_port = device_port
        self.camera = cv2.VideoCapture(0)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.presenca_detectada = False
        self.ultima_presenca = time.time()
        self.ultimo_envio = 0

    def detectar_presenca(self):
        """Verifica se há presença utilizando a câmera."""
        ret, frame = self.camera.read()
        if not ret:
            print("Erro ao acessar a câmera!")
            return

        imagem_cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rostos = self.face_cascade.detectMultiScale(imagem_cinza, scaleFactor=1.2, minNeighbors=5)
        if len(rostos) > 0:
            self.presenca_detectada = True
            self.ultima_presenca = time.time()
        else:
            self.presenca_detectada = time.time() - self.ultima_presenca <= 15

    def enviar_dados(self):
        """Envia os dados de presença para o gateway via UDP multicast."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        while True:
            self.detectar_presenca()
            agora = time.time()

            if agora - self.ultimo_envio >= 15:
                estado = "detectada" if self.presenca_detectada else "não detectada"
                print(f"Presença {estado}. Enviando dados ao gateway...")

                discovery_message = device_pb2.DeviceDiscovery(
                    device_id=self.device_id,
                    device_ip=self.device_ip,
                    device_port=self.device_port,
                    device_type="sensor_presenca",
                    state="ligado" if self.presenca_detectada else "desligado",
                )

                message = discovery_message.SerializeToString()
                sock.sendto(message, (MCAST_GROUP, MCAST_PORT))
                self.ultimo_envio = agora  # Atualiza o timestamp do último envio

            time.sleep(1)

    def liberar_camera(self):
        """Libera a câmera ao finalizar o programa."""
        self.camera.release()


if __name__ == "__main__":
    sensor = PresencaSensor(device_id="sensor_presenca_001", device_ip="192.168.1.100", device_port=6000)
    try:
        sensor.enviar_dados()
    except KeyboardInterrupt:
        print("Encerrando o sensor de presença.")
        sensor.liberar_camera()
def detect_presence():
    """Função para simular a detecção de presença."""
    return random.choice(["entrando", "saindo", "nenhum"])

def send_presence_data(device_id, device_ip, device_port):
    """Envia os dados de presença para o gateway via multicast."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    group = socket.inet_aton(MCAST_GROUP)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        presence = detect_presence()

        discovery_message = device_pb2.DeviceDiscovery(
            device_id=device_id,
            device_ip=device_ip,
            device_port=device_port,
            device_type="sensor_presenca",
            state=presence
        )

        message = discovery_message.SerializeToString()
        print(f"Enviando dados para o gateway: Sensor {device_id}, Presença: {presence}")
        
        sock.sendto(message, (MCAST_GROUP, MCAST_PORT))
        
        time.sleep(5)

def main():
    device_id = "sensor_presenca_1"
    device_ip = "192.168.0.12"
    device_port = 6002
    send_presence_data(device_id, device_ip, device_port)

if __name__ == "__main__":
    main()
