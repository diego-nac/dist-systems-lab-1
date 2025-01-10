from smart_devices.Lamp import Lamp
from utils import *

lamp = Lamp(device_id="2", device_name="Living Room Lamp", is_on=False, brightness=0.5, color="blue")

lamp.show_commands()
logger.info(lamp.process_command("ligar"))
logger.info(f"Lamp status: {lamp}")
logger.info(lamp.process_command("ajustar brilho 0.8"))
logger.info(lamp.process_command("alterar cor red"))
logger.info(f"Updated Lamp status: {lamp}")
lamp.start()
