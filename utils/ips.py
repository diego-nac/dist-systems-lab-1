import socket
import random

def get_local_ip():
    """Obtém o endereço IP local da máquina."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Testa a conexão com um servidor público para descobrir o IP local
        sock.connect(("8.8.8.8", 80))
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except Exception as e:
        print(f"Erro ao obter o IP local: {e}")
        return "127.0.0.1"  # Fallback para localhost

def generate_multicast_group():
    """Gera um endereço de grupo multicast válido (224.0.0.0 - 239.255.255.255)."""
    return f"239.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def is_ip_in_use(ip, port=5006):
    """
    Verifica se o IP e a porta estão em uso na rede local.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.1)  # Timeout curto para não bloquear
            result = sock.connect_ex((ip, port))
            return result == 0  # Retorna True se o IP e porta estiverem em uso
    except Exception:
        return False

def generate_device_ip(local_ip, offset, max_attempts=10):
    """
    Gera um IP único para o dispositivo, evitando duplicações.
    """
    octets = local_ip.split('.')
    if len(octets) != 4:
        raise ValueError("IP local inválido")
    
    base_octet = int(octets[-1])
    for attempt in range(max_attempts):
        proposed_ip = '.'.join(octets[:3] + [str(base_octet + offset + attempt)])
        if not is_ip_in_use(proposed_ip):
            return proposed_ip

    raise RuntimeError("Não foi possível gerar um IP único após várias tentativas")

