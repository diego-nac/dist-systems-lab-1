from .ips import *

# Configuração de multicast
MCAST_GROUP = '239.1.1.1'
MCAST_PORT = 7000
BUFFER_SIZE = 2048
DISCOVERY_DELAY = 5
LOCAL_IP = get_local_ip()  # IP dinâmico da máquina

# Configurações específicas para dispositivos
CLIENT_IP = generate_ip(1)  # IP privado do cliente
GATEWAY_IP = generate_ip(2)  # IP privado do gateway
LAMP_IP = generate_ip(3)  # IP privado da lâmpada
MOTION_SENSOR_IP = generate_ip(4)  # IP privado da lâmpada


# Porta para conexões TCP
DEVICES_PORT = 5006

# Configurações gerais
PROJECT_NAME = "Smart Home"
