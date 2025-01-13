from smart_devices.abstract.SmartDevice import SmartDevice
from utils import *
import smart_devices.proto.smart_devices_pb2 as proto  # Importação do Protobuf

class Lamp(SmartDevice):
    VALID_COLORS = {"white", "red", "blue", "green", "yellow", "purple", "orange"}

    def __init__(self, device_id: str, device_name: str, is_on: bool = False, brightness: float = 0.8, color: str = "white", device_ip: str = DEVICES_IP, device_port: int = DEVICES_PORT):
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
        logger.warning(f"Invalid color '{color}'. Defaulting to 'white'.")
        return "white"

    # Getter and Setter for Brightness
    @property
    def brightness(self) -> float:
        return self._brightness

    @brightness.setter
    def brightness(self, value: float):
        if 0.0 <= value <= 1.0:
            self._brightness = value
            logger.info(f"Brightness set to {self._brightness * 100:.0f}% for Lamp({self.id}:{self.name}).")
        else:
            logger.warning("Brightness value must be between 0.0 and 1.0.")

    # Getter and Setter for Color
    @property
    def color(self) -> str:
        return self._color

    @color.setter
    def color(self, value: str):
        validated_color = self._validate_color(value)
        self._color = validated_color
        logger.info(f"Color set to {self._color} for Lamp({self.id}:{self.name}).")

    # Getter and Setter for On/Off State
    @property
    def is_on(self) -> bool:
        return self._is_on

    @is_on.setter
    def is_on(self, value: bool):
        self._is_on = value
        state = "ON" if value else "OFF"
        logger.info(f"Lamp({self.id}:{self.name}) turned {state}.")

    def process_command(self, command: str):
        parts = command.lower().split()
        if len(parts) == 0:
            return "Invalid command."

        action = parts[0]

        if action == "ligar":
            self.is_on = True
            return f"Lamp {self.name} is now ON."

        elif action == "desligar":
            self.is_on = False
            return f"Lamp {self.name} is now OFF."

        elif action == "ajustar" and len(parts) > 2 and parts[1] == "brilho":
            try:
                brightness = float(parts[2])
                self.brightness = brightness  # Uses the setter
                return f"Brightness of lamp {self.name} adjusted to {self.brightness * 100:.0f}%"
            except ValueError:
                return "Invalid brightness value."

        elif action == "alterar" and len(parts) > 1 and parts[1] == "cor":
            if len(parts) > 2:
                color = parts[2]
                self.color = color  # Uses the setter
                return f"Lamp {self.name} color changed to {self.color}."
            else:
                return "Please specify a color."

        else:
            return "Invalid command for lamp."

    def show_commands(self):
        logger.info(f"Commands for Lamp({self.id}:{self.name}): {', '.join(self.commands)}")

    def to_proto(self) -> proto.DeviceDiscovery:
        """
        Serializa o estado da lâmpada em uma mensagem Protobuf.
        """
        return proto.DeviceDiscovery(
            device_id=self.id,
            device_name=self.name,
            device_type=self.type,
            is_on=self.is_on,
            brightness=self.brightness,
            color=self.color,
            device_ip=self.ip,
            device_port=self.port
        )

    def __str__(self):
        state_str = "ON" if self.is_on else "OFF"
        return f"Lamp(ID: {self.id}, Name: {self.name}, State: {state_str}, Brightness: {self.brightness * 100:.0f}%, Color: {self.color}, IP: {self.ip}, Port: {self.port})"
