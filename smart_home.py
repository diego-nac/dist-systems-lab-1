from threading import Thread
from smart_devices.Lamp import Lamp
from smart_devices.MotionSensor import MotionSensor
from utils import *


def initialize_devices():
    # Criar e inicializar dispositivos
    devices = []

    # Lâmpada
    lamp = Lamp(device_id="1", device_name="Living Room Lamp", is_on=False,
                brightness=0.5, color="blue", device_port=DEVICES_PORT, device_ip=LAMP_IP)
    devices.append(lamp)
    Thread(target=lamp.start, daemon=True).start()

    # Sensor de Movimento
    motion_sensor = MotionSensor(
        device_id="2",
        device_name="Living Room Motion Sensor",
        device_ip=MOTION_SENSOR_IP,
        device_port=DEVICES_PORT
    )
    devices.append(motion_sensor)
    Thread(target=motion_sensor.detect_motion, daemon=True).start()

    print("Dispositivos inicializados:")
    for device in devices:
        print(device)


if __name__ == "__main__":
    print("Inicializando sistema de casa inteligente...")
    initialize_devices()

    # Manter o script ativo
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Sistema encerrado pelo usuário.")
