from smart_devices.abstract import SmartDevice
from typing import Dict, Any
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

    def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        action = command.get("action")
        if action == "reset":
            self.update_state("motion_detected", False)
            return {"status": "success", "message": "Motion sensor reset."}
        return {"status": "error", "message": "Invalid action."}

    def get_status(self) -> Dict[str, Any]:
        return {
            "device_id": self._id,
            
            "device_name": self._name,
            "device_type": self._type,
            "state": self._state 
        }
