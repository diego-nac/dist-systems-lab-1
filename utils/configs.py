from .ips import *

# Configuração de multicast
MCAST_GROUP = '239.1.1.1'
MCAST_PORT = 7000
BUFFER_SIZE = 2048
DISCOVERY_DELAY = 2
LOCAL_IP = get_local_ip()  # Deve ser o IP da máquina que está rodando

# Configurações específicas para dispositivos
LAMP_IP = generate_device_ip(LOCAL_IP, 10)
MOTION_SENSOR_IP = generate_device_ip(LOCAL_IP, 5)
DEVICES_PORT = 5006

# Configurações gerais
PROJECT_NAME = "Smart Home"
