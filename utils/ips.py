
import socket
import random

def get_local_ip():
    """Obtém o endereço IP local da máquina."""
    try:
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except Exception as e:
        print(f"Erro ao obter o IP local: {e}")
        return "127.0.0.1"  

def generate_multicast_group():
    """Gera um endereço de grupo multicast válido (224.0.0.0 - 239.255.255.255)."""
    return f"239.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 255)}"


# Função para gerar IPs dos dispositivos com base no IP local
def generate_device_ip(local_ip, offset):
    """Gera um IP de dispositivo baseado no IP local e um offset."""
    octets = local_ip.split('.')
    if len(octets) != 4:
        raise ValueError("IP local inválido")
    octets[-1] = str(int(octets[-1]) + offset)
    return '.'.join(octets)
