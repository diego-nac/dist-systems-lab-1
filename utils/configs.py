# from .ips import *

# # Configuração de multicast
# MCAST_GROUP = '239.1.1.1'
# MCAST_PORT = 7000
# BUFFER_SIZE = 2048
# DISCOVERY_DELAY = 2
# LOCAL_IP = get_local_ip()  # Deve ser o IP da máquina que está rodando

# # Configurações específicas para dispositivos
# LAMP_IP = generate_device_ip(LOCAL_IP, 10)
# MOTION_SENSOR_IP = generate_device_ip(LOCAL_IP, 5)
# DEVICES_PORT = 5006

# # Configurações gerais
# PROJECT_NAME = "Smart Home"


from .ips import *

# Configuração de multicast
MCAST_GROUP = '239.1.1.1'
MCAST_PORT = 7000
BUFFER_SIZE = 2048
DISCOVERY_DELAY = 5
LOCAL_IP = get_local_ip()  # Deve ser o IP da máquina que está rodando

# Configurações específicas para dispositivos
CLIENT_IP = "172.31.93.178"  # IP público da instância do client
GATEWAY_IP = "172.31.82.96"  # IP público da instância do gateway
LAMP_IP = "172.31.87.242"  # IP público da instância da lâmpada

# Porta padrão para dispositivos
DEVICES_PORT = 7000

# Configurações gerais
PROJECT_NAME = "Smart Home"
