from smart_devices.abstract.SmartDevice import SmartDevice
from utils import *
import smart_devices.proto.smart_devices_pb2 as proto  # Importação do Protobuf
from threading import Thread
import cv2
import time

class MotionSensor(SmartDevice):
    def __init__(self, device_id: str, device_name: str, device_ip: str = MOTION_SENSOR_IP, device_port: int = DEVICES_PORT):
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            device_type="MotionSensor",
            is_on=True,  # Sensores normalmente estão sempre "ligados"
            device_ip=device_ip,
            device_port=device_port
        )
        self._motion_detected = False
        self._camera = cv2.VideoCapture(0)
        self._face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def detect_motion(self):
        """Detecta movimento utilizando a câmera."""
        ret, frame = self._camera.read()
        if not ret:
            logger.warning("Erro ao acessar a câmera do sensor de movimento.")
            return

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._face_cascade.detectMultiScale(gray_frame, scaleFactor=1.2, minNeighbors=5)
        self._motion_detected = len(faces) > 0

    def send_state_periodically(self):
        """Envia o estado do sensor ao Gateway periodicamente via multicast."""
        while True:
            self.detect_motion()
            discovery_message = self.to_proto()

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                message = discovery_message.SerializeToString()
                logger.info(f"[Multicast] Enviando estado do MotionSensor {self.id} para {MCAST_GROUP}:{MCAST_PORT}")
                sock.sendto(message, (MCAST_GROUP, MCAST_PORT))

            # Log do estado do dispositivo
            logger.debug(f"Estado do MotionSensor {self.name}:")
            logger.debug(f"  - Ligado: {'Sim' if self.is_on else 'Não'}")
            logger.debug(f"  - Movimento Detectado: {'Sim' if self._motion_detected else 'Não'}")
            logger.debug(f"  - IP: {self.ip}")
            logger.debug(f"  - Porta: {self.port}")

            time.sleep(15)  # Envia estado a cada 15 segundos


    def process_command(self, device_command: proto.DeviceCommand):
        """Processa comandos enviados ao sensor."""
        action = device_command.command.lower()
        logger.debug(f"Comando recebido: {action} para {self.name}")
        if action == "ligar":
            self.is_on = True
            logger.info(f"{self.name}: Estado atualizado para ligado.")
            return f"Sensor de movimento {self.name} ligado."
        elif action == "desligar":
            self.is_on = False
            logger.info(f"{self.name}: Estado atualizado para desligado.")
            return f"Sensor de movimento {self.name} desligado."
        else:
            logger.warning(f"{self.name}: Comando inválido recebido.")
            return f"Comando inválido para o sensor de movimento: {action}"


    def to_proto(self) -> proto.DeviceDiscovery:
        """Serializa o estado do sensor em uma mensagem Protobuf."""
        proto_message = proto.DeviceDiscovery(
            device_id=self.id,
            device_name=self.name,
            device_type=self.type,
            is_on=self.is_on,
            device_ip=self.ip,
            device_port=self.port,
            motion_detected=self._motion_detected
        )
        
        logger.info(f"Mensagem Protobuf gerada: {proto_message}")
        return proto_message

    def __del__(self):
        """Libera a câmera ao finalizar o processo."""
        self._camera.release()