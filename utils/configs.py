from .ips import get_local_ip, generate_ip
from .files import import_ips_from_json

# Configuração de multicast
MCAST_GROUP = '239.1.1.1'
MCAST_PORT = 7000
BUFFER_SIZE = 2048
DISCOVERY_DELAY = 5
LOCAL_IP = get_local_ip()  # IP dinâmico da máquina

# use a função generate_valid_ips(count) para gerar os ips dos dispositivos e coloque aqui
# ['192.168.1.8', '192.168.1.9', '192.168.1.10', '192.168.1.11', '192.168.1.12']

VALID_IPS = import_ips_from_json()


CLIENT_IP = VALID_IPS[0] 
GATEWAY_IP = VALID_IPS[1] 
LAMP_IP = VALID_IPS[2] 
MOTION_SENSOR_IP = VALID_IPS[3] 
TEMPERATURE_SENSOR_IP = VALID_IPS[4]

# Porta para conexões TCP
DEVICES_PORT = 5006

# Configurações gerais
PROJECT_NAME = "Smart Home"
