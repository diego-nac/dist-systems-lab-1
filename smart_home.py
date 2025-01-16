from smart_devices.Lamp import Lamp
from utils import *

lamp = Lamp(device_id="1", device_name="Living Room Lamp", is_on=False, brightness=0.5, color="blue", device_port=DEVICES_PORT, device_ip=DEVICES_IP)
lamp.start()