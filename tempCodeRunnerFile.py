ensor = MotionSensor(
    device_id="sensor_001",
    device_name="Living Room Sensor",
    device_ip="192.168.0.12",
    device_port=6002
)
print(motion_sensor)

# Inicia o sensor
motion_sensor.start()