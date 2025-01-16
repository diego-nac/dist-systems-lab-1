from smart_devices.abstract.SmartDevice import SmartDevice
from utils import *
import smart_devices.proto.smart_devices_pb2 as proto  # Importação do Protobuf
from threading import Thread

class Lamp(SmartDevice):
    VALID_COLORS = {"white", "red", "blue", "green", "yellow", "purple", "orange"}

    def __init__(self, device_id: str, device_name: str, is_on: bool = False, brightness: float = 0.8, color: str = "white", device_ip: str = LAMP_IP, device_port: int = DEVICES_PORT):
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            device_type="Lamp",
            is_on=is_on,
            device_ip=device_ip,
            device_port=device_port
        )
        self._brightness = max(0.0, min(1.0, brightness))
        self._color = self._validate_color(color)
        self.commands = ["ligar", "desligar", "ajustar brilho", "alterar cor"]

    def _validate_color(self, color: str) -> str:
        if color.lower() in self.VALID_COLORS:
            return color.lower()
        logger.warning(f"Cor inválida '{color}'. Usando 'white' como padrão.")
        return "white"

    # Getter and Setter for Brightness
    @property
    def brightness(self) -> float:
        return self._brightness

    @brightness.setter
    def brightness(self, value: float):
        if 0.0 <= value <= 1.0:
            self._brightness = value
            logger.info(f"Brilho ajustado para {self._brightness * 100:.0f}% na Lâmpada ({self.id}:{self.name}).")
        else:
            logger.warning("O valor de brilho deve estar entre 0.0 e 1.0.")

    # Getter and Setter for Color
    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str):
        validated_color = self._validate_color(value)
        self._color = validated_color
        logger.info(f"Cor ajustada para {self._color} na Lâmpada ({self.id}:{self.name}).")

    # Getter and Setter for On/Off State
    @property
    def is_on(self) -> bool:
        return self._is_on

    @is_on.setter
    def is_on(self, value: bool):
        self._is_on = value
        state = "ON" if value else "OFF"
        logger.info(f"Lâmpada ({self.id}:{self.name}) foi {state}.")
    def process_command(self, device_command: proto.DeviceCommand):
        """
        Processa comandos recebidos no formato Protobuf e reinicia o envio do estado do dispositivo.
        """
        action = device_command.command.lower()

        if action == "ligar":
            self.is_on = True
            Thread(target=self.start_multicast, daemon=True).start()
            return f"Lâmpada {self.name} agora está LIGADA."

        elif action == "desligar":
            self.is_on = False
            Thread(target=self.start_multicast, daemon=True).start()
            return f"Lâmpada {self.name} agora está DESLIGADA."

        elif action == "brightness":
            try:
                brightness = device_command.brightness
                if 0.0 <= brightness <= 100.0:
                    self.brightness = round((brightness / 100),2)  # Normaliza para 0.0-1.0
                    logger.info(f"Luminosidade ajustada para {self.brightness * 100:.0f}% na lâmpada {self.name}.")
                    Thread(target=self.start_multicast, daemon=True).start()
                    return f"Brilho da lâmpada {self.name} ajustado para {self.brightness * 100:.0f}%"
                else:
                    return "O valor de brilho deve estar entre 0 e 100."
            except ValueError:
                return "Valor de brilho inválido."
            
        elif action == "alterar cor":
            color = device_command.color
            if color.lower() in self.VALID_COLORS:
                self.color = color.lower()
                logger.info(f"Cor alterada para {self.color} na lâmpada {self.name}.")
                Thread(target=self.start_multicast, daemon=True).start()
                return f"Cor da lâmpada {self.name} alterada para {self.color}."
            else:
                return f"Cor inválida '{color}'."

        else:
            return "Comando inválido para a lâmpada."
    def show_commands(self):
        logger.info(f"Comandos disponíveis para Lâmpada ({self.id}:{self.name}): {', '.join(self.commands)}")

    def to_proto(self) -> proto.DeviceDiscovery:
        """
        Serializa o estado da lâmpada em uma mensagem Protobuf.
        """
        proto_message = proto.DeviceDiscovery(
            device_id=self.id,
            device_name=self.name,
            device_type=self.type,
            is_on=self.is_on,
            brightness=self.brightness,
            color=self.color,
            device_ip=self.ip,
            device_port=self.port
        )
        logger.info(f"Mensagem Protobuf gerada: {proto_message}")
        return proto_message

    def __str__(self):
        state_str = "ON" if self.is_on else "OFF"
        return f"Lamp(ID: {self.id}, Name: {self.name}, State: {state_str}, Brightness: {self.brightness * 100:.0f}%, Color: {self.color}, IP: {self.ip}, Port: {self.port})"
