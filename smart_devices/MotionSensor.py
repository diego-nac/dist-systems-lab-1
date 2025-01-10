from smart_devices.abstract.SmartDevice import SmartDevice
from utils import *

class MotionSensor(SmartDevice):
    def __init__(self, device_id: str, device_name: str, is_on: bool = False, device_ip: str = IP_DEVICES, device_port: int = '1111'):
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            device_type="MotionSensor",
            is_on = is_on,
            device_ip=device_ip,
            device_port=device_port
        )
        self.commands = ["ligar", "desligar"]

    def process_command(self, command: str):
        command = command.lower()
        if command == "ligar":
            self.is_on = True
            return "Motion sensor is ON"
        elif command == "desligar":
            self.is_on = False
            return "Motion sensor is OFF"
        else:
            return "Invalid command for motion sensor"
        
    def show_commands(self):
        logger.info(f"Commands for MotionSensor({self._id}:{self._name}): {', '.join(self.commands)}")
    
        