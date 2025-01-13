from smart_devices.abstract.SmartDevice import SmartDevice
from utils import *
import smart_devices.proto.smart_devices_pb2 as proto  # Importação do Protobuf

class MotionSensor(SmartDevice):
    def __init__(self, device_id: str, device_name: str, is_on: bool = False, device_ip: str = IP_DEVICES, device_port: int = 1111):
        super().__init__(
            device_id=device_id,
            device_name=device_name,
            device_type="MotionSensor",
            is_on=is_on,
            device_ip=device_ip,
            device_port=device_port
        )
        self.commands = ["ligar", "desligar"]

    def process_command(self, command: str):
        command = command.lower()
        if command == "ligar":
            self.is_on = True
            return f"Motion sensor {self.name} is ON"
        elif command == "desligar":
            self.is_on = False
            return f"Motion sensor {self.name} is OFF"
        else:
            return "Invalid command for motion sensor"

    def show_commands(self):
        logger.info(f"Commands for MotionSensor({self._id}:{self._name}): {', '.join(self.commands)}")

    def to_proto(self) -> proto.DeviceDiscovery:
        """
        Serializa o estado do sensor de movimento em uma mensagem Protobuf.
        """
        return proto.DeviceDiscovery(
            device_id=self.id,
            device_name=self.name,
            device_type=self.type,
            is_on=self.is_on,
            device_ip=self.ip,
            device_port=self.port
        )

    def __str__(self):
        state_str = "ON" if self.is_on else "OFF"
        return f"MotionSensor(ID: {self.id}, Name: {self.name}, State: {state_str}, IP: {self.ip}, Port: {self.port})"
