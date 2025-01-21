from smart_devices.abstract.SmartDevice import SmartDevice
from utils import logger, MCAST_GROUP, MCAST_PORT, DEVICES_PORT, TEMPERATURE_SENSOR_IP
import smart_devices.proto.smart_devices_pb2 as proto  # Importação do Protobuf
import socket
import time
import random  # Para simular leituras de temperatura

class TemperatureSensor(SmartDevice):
    def __init__(self, device_id: str, device_name: str, device_ip: str = TEMPERATURE_SENSOR_IP, device_port: int = DEVICES_PORT):
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            device_type="TemperatureSensor",
            is_on=True,  # Sensores normalmente estão sempre "ligados"
            device_ip=device_ip,
            device_port=device_port
        )
        self._temperature = 25.0  # Temperatura inicial (°C)

    def read_temperature(self):
        """Simula a leitura da temperatura. Substitua com leitura real do sensor se aplicável."""
        if self.is_on:
            # Simulação: variação aleatória da temperatura
            self._temperature += random.uniform(-0.5, 0.5)
            self._temperature = round(self._temperature, 2)
            logger.debug(f"Temperatura lida: {self._temperature}°C")
        else:
            logger.debug("Sensor desligado. Não lendo temperatura.")

    def send_state_periodically(self):
        """Envia o estado do sensor ao Gateway periodicamente via multicast."""
        while True:
            self.read_temperature()
            discovery_message = self.to_proto()

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.ip))
                message = discovery_message.SerializeToString()
                logger.info(f"[Multicast] Enviando estado do TemperatureSensor {self.id} para {MCAST_GROUP}:{MCAST_PORT}")
                sock.sendto(message, (MCAST_GROUP, MCAST_PORT))

            # Log do estado do dispositivo
            logger.debug(f"Estado do TemperatureSensor {self.name}:")
            logger.debug(f"  - Ligado: {'Sim' if self.is_on else 'Não'}")
            logger.debug(f"  - Temperatura Atual: {self._temperature}°C")
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
            return f"Sensor de temperatura {self.name} ligado."
        elif action == "desligar":
            self.is_on = False
            logger.info(f"{self.name}: Estado atualizado para desligado.")
            return f"Sensor de temperatura {self.name} desligado."
        else:
            logger.warning(f"{self.name}: Comando inválido recebido.")
            return f"Comando inválido para o sensor de temperatura: {action}"

    def to_proto(self) -> proto.DeviceDiscovery:
        """Serializa o estado do sensor em uma mensagem Protobuf."""
        proto_message = proto.DeviceDiscovery(
            device_id=self.id,
            device_name=self.name,
            device_type=self.type,
            is_on=self.is_on,
            device_ip=self.ip,
            device_port=self.port,
            temperature=self._temperature  # Adiciona a temperatura ao Protobuf
        )
        
        logger.info(f"Mensagem Protobuf gerada: {proto_message}")
        return proto_message

    def __del__(self):
        """Limpeza ao finalizar o processo."""
        logger.info(f"Finalizando TemperatureSensor {self.name}.")
        super().__del__()

