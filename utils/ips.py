import ipaddress
import subprocess
import platform
from socket import gethostbyname, gethostname, inet_aton, error, AF_INET
from psutil import net_if_addrs
import random

def get_local_ip():
    return gethostbyname(gethostname())

def get_local_ip_and_subnet_mask():
    local_ip = get_local_ip()
    for _, addrs in net_if_addrs().items():
        for addr in addrs:
            if addr.family == AF_INET and addr.address == local_ip:
                return local_ip, addr.netmask
    return None, None

def is_ip_valid(ip):
    try:
        inet_aton(ip)
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", ip]
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except error:
        return False

def list_ips():
    local_ip, subnet_mask = get_local_ip_and_subnet_mask()
    if not local_ip or not subnet_mask:
        raise ValueError("Não foi possível obter o IP local ou a máscara de rede.")
    network = ipaddress.IPv4Network(f"{local_ip}/{subnet_mask}", strict=False)
    hosts = list(network.hosts())
    return [str(host) for host in hosts]

def generate_ip(offset):
    available_ips = list_ips()
    if offset < 0 or offset >= len(available_ips):
        raise ValueError(f"O offset fornecido ({offset}) está fora do intervalo da rede.")
    for i in range(offset, len(available_ips)):
        candidate_ip = available_ips[i]
        if is_ip_valid(candidate_ip):
            return candidate_ip
    raise ValueError("Não foi possível encontrar um IP válido e não utilizado na rede.")


def generate_multicast_group():
    return f"239.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
