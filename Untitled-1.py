# %%
from conn.connection import ConnectionManager

from socket import gethostbyname, gethostname, AF_INET
from psutil import net_if_addrs
from socket import inet_aton, socket, AF_INET, SOCK_STREAM, error
from socket import gethostbyname, gethostname, AF_INET, SOCK_STREAM, error
from psutil import net_if_addrs


# %%
import ipaddress
import time
from socket import error

# %%
from utils import *

# %%
con = ConnectionManager()

# %%
def callback_fun(msg, add):
    print(msg,add)

# %%
con.start_tcp_server(callback_function=callback_fun)

# %%

def get_local_ip():
    return gethostbyname(gethostname())


def get_local_ip_and_subnet_mask():
    local_ip = get_local_ip()
    for iface, addrs in net_if_addrs().items():
        for addr in addrs:
            if addr.family == AF_INET and addr.address == local_ip:
                return local_ip, addr.netmask
    return None, None


def is_ip_valid_and_available(ip):
    try:
        socket.inet_aton(ip)
        for iface, addrs in net_if_addrs().items():
            for addr in addrs:
                if addr.family == AF_INET and addr.address == ip:
                    return True  
        with socket.socket(AF_INET, SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((ip, 80))
            return result == 0
    except error:
        return False


def generate_ip_with_offset(offset):
    local_ip, subnet_mask = get_local_ip_and_subnet_mask()
    if not local_ip or not subnet_mask:
        raise ValueError("Não foi possível obter o IP local ou a máscara de rede.")

    # Calcula a rede a partir do IP local e da máscara de sub-rede
    network = ipaddress.IPv4Network(f"{local_ip}/{subnet_mask}", strict=False)
    hosts = list(network.hosts())
    print(len(hosts))
    

    if offset < 0 or offset >= len(hosts):
        raise ValueError(f"O offset fornecido ({offset}) está fora do intervalo da rede.")

    # Loop até encontrar um IP válido e disponível
    for i in range(offset, len(hosts)):
        candidate_ip = str(hosts[i])
        print(f"Testando IP: {candidate_ip}")
        if is_ip_valid_and_available(candidate_ip):
            return candidate_ip

    raise ValueError("Não foi possível encontrar um IP válido e disponível na rede.")


# %%
print(generate_ip_with_offset(1))



