import ipaddress
import subprocess
import platform
from socket import inet_aton, error, AF_INET, socket, SOCK_DGRAM
from psutil import net_if_addrs
import random
from .LoggerConfig import LoggerConfig


logger = LoggerConfig("IPConfig").get_logger()

def get_local_ip():
    with socket(AF_INET, SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1" 


def get_local_ip_and_subnet_mask():
    logger.debug("Obtendo IP local e máscara de rede...")
    local_ip = get_local_ip()
    for _, addrs in net_if_addrs().items():
        for addr in addrs:
            if addr.family == AF_INET and addr.address == local_ip:
                logger.debug(f"IP local e máscara de rede obtidos: {local_ip}, {addr.netmask}")
                return local_ip, addr.netmask
    return None, None

def is_ip_valid(ip):
    logger.debug(f"Verificando se o IP {ip} é válido...")
    try:
        inet_aton(ip)
        param = "-n" if platform.system().lower() == "windows" else "-c"
        command = ["ping", param, "1", ip]
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) != 0
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
    logger.debug(f"Gerando IP com offset {offset}...")
    available_ips = list_ips()  
    if offset < 0 or offset >= len(available_ips):
        raise ValueError(f"O offset fornecido ({offset}) está fora do intervalo da rede.")
    for i in range(offset, len(available_ips)):
        candidate_ip = available_ips[i]
        if is_ip_valid(candidate_ip):  
            logger.debug(f"IP livre encontrado: {candidate_ip}")
            if configure_ip(candidate_ip):
                return candidate_ip
    raise ValueError("Não foi possível encontrar um IP livre na rede.")

def generate_valid_ips(count):
    try:
        logger.debug(f"Gerando até {count} IPs válidos configurados...")
        available_ips = list_ips()
        valid_ips = []

        for ip in available_ips:
            if len(valid_ips) >= count:
                break
            if is_ip_valid(ip) and configure_ip(ip):
                valid_ips.append(ip)
                logger.debug(f"IP configurado: {ip}")

        if len(valid_ips) < count:
            raise ValueError(f"Não foi possível gerar a quantidade necessária de IPs ({count}).")

        return valid_ips
    except Exception as e:
        logger.error(f"Erro ao gerar IPs válidos configurados: {e}")
        return []



def generate_multicast_group():
    return f"239.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"




def is_ip_configured(ip: str) -> bool:
    try:
        for _, addrs in net_if_addrs().items():
            for addr in addrs:
                if addr.family == AF_INET and addr.address == ip:
                    return True
        return False
    except Exception as e:
        logger.error(f"Erro ao verificar se o IP {ip} está configurado: {e}")
        return False

def get_network_interface(subnet: str = "192.168.1.") -> str:
    try:
        for iface, addrs in net_if_addrs().items():
            for addr in addrs:
                if addr.family == AF_INET and addr.address.startswith(subnet):
                    return iface
        raise RuntimeError(f"Nenhuma interface encontrada na sub-rede {subnet}")
    except Exception as e:
        logger.error(f"Erro ao buscar a interface de rede para a sub-rede {subnet}: {e}")
        raise

def configure_ip(ip: str) -> None:
    try:
        if is_ip_configured(ip):
            logger.debug(f"O IP {ip} já está configurado.")
            return True

        system = platform.system().lower()

        if system == "linux":
            interface = get_network_interface()
            command = ["sudo", "ip", "addr", "add", f"{ip}/24", "dev", interface]
            subprocess.run(command, check=True)
            logger.debug(f"IP {ip} atribuído com sucesso à interface {interface}.")
            return True

        elif system == "windows":
            interface = get_network_interface()
            command = [
                "netsh", "interface", "ip", "add", "address", interface, ip, "255.255.255.0"
            ]
            subprocess.run(command, check=True)
            logger.debug(f"IP {ip} atribuído com sucesso à interface {interface}.")
            return True

        else:
            raise NotImplementedError(f"Sistema operacional não suportado: {system}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar o comando para atribuir o IP {ip}: {e}")
    except Exception as e:
        logger.error(f"Erro geral ao configurar o IP {ip}: {e}")
        return False