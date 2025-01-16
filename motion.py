from smart_devices.MotionSensor import MotionSensor
from utils import *

# Criação e inicialização do sensor de movimento
motion_sensor = MotionSensor(
    device_id="2",
    device_name="Living Room Motion Sensor",
    device_ip=MOTION_SENSOR_IP,
    device_port=DEVICES_PORT+1
)

# Início do sensor
motion_sensor.start()
