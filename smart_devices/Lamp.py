from smart_devices.abstract.SmartDevice import SmartDevice
from utils import *

class Lamp(SmartDevice):
    VALID_COLORS = {"white", "red", "blue", "green", "yellow", "purple", "orange"}

    def __init__(self, device_id: str, device_name: str, is_on: bool = False, brightness: float = 0.8, color: str = "white", device_ip: str = IP_DEVICES, device_port: int = 1111):
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            device_type="Lamp",
            is_on=is_on,
            device_ip=device_ip,
            device_port=device_port
        )
        self.brightness = max(0.0, min(1.0, brightness))
        self.color = self._validate_color(color)
        self.commands = ["ligar", "desligar", "ajustar brilho", "alterar cor"]

    def _validate_color(self, color: str) -> str:
        if color.lower() in self.VALID_COLORS:
            return color.lower()
        logger.warning(f"Invalid color '{color}'. Defaulting to 'white'.")
        return "white"

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
                if 0.0 <= brightness <= 1.0:
                    self.brightness = brightness
                    return f"Brightness of lamp {self.name} adjusted to {self.brightness * 100:.0f}%"
                else:
                    return "Brightness value must be between 0.0 and 1.0."
            except ValueError:
                return "Invalid brightness value."

        elif action == "alterar" and len(parts) > 1 and parts[1] == "cor":
            if len(parts) > 2:
                color = parts[2]
                self.color = self._validate_color(color)
                return f"Lamp {self.name} color changed to {self.color}."
            else:
                return "Please specify a color."

        else:
            return "Invalid command for lamp."

    def show_commands(self):
        logger.info(f"Commands for Lamp({self.id}:{self.name}): {', '.join(self.commands)}")

    def __str__(self):
        state_str = "ON" if self.is_on else "OFF"
        return f"Lamp(ID: {self.id}, Name: {self.name}, State: {state_str}, Brightness: {self.brightness * 100:.0f}%, Color: {self.color}, IP: {self.ip}, Port: {self.port})"
