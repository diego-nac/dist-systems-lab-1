from .ips import *

# Configuração de multicast
MCAST_GROUP = '239.1.1.1'
MCAST_PORT = 7000
BUFFER_SIZE = 2048
DISCOVERY_DELAY = 5
LOCAL_IP = get_local_ip()  # IP dinâmico da máquina

# Configurações específicas para dispositivos
CLIENT_IP = "172.31.93.178"  # IP privado do cliente
GATEWAY_IP = "172.31.82.96"  # IP privado do gateway
LAMP_IP = "172.31.87.242"  # IP privado da lâmpada

# Porta para conexões TCP
DEVICES_PORT = 5006

# Configurações gerais
PROJECT_NAME = "Smart Home"
