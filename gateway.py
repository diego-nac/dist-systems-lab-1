import socket
import threading
import time
from google.protobuf.message import DecodeError
from device_pb2 import DiscoveryMessage, DeviceRequest, DeviceResponse, SensorData, GatewayReport

# Configurações do Gateway
UDP_MULTICAST_GROUP = "239.255.255.250"
UDP_MULTICAST_PORT = 12345
TCP_SERVER_PORT = 54321

discovered_devices = {}
"""
Estrutura:
{
    id: {
        "device_type": str,
        "ip": str,
        "port": int,
        "active": bool
    }
}
"""

def handle_udp_multicast():
    """
    Manipula as mensagens de descoberta enviadas pelos dispositivos via UDP multicast.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as udp_socket:
        udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        udp_socket.bind(("", UDP_MULTICAST_PORT))

        multicast_request = socket.inet_aton(UDP_MULTICAST_GROUP) + socket.inet_aton("0.0.0.0")
        udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)

        print(f"[INFO] Aguardando mensagens de descoberta na porta {UDP_MULTICAST_PORT}...")

        while True:
            data, addr = udp_socket.recvfrom(1024)
            try:
                discovery_message = DiscoveryMessage()
                discovery_message.ParseFromString(data)

                discovered_devices[discovery_message.id] = {
                    "device_type": discovery_message.device_type,
                    "ip": discovery_message.ip,
                    "port": discovery_message.port,
                    "active": discovery_message.active
                }

                print(f"[INFO] Dispositivo descoberto: {discovery_message}")
            except DecodeError as e:
                print(f"[ERRO] Falha ao decodificar mensagem UDP: {e}")

def send_udp_multicast_request():
    """
    Envia solicitação multicast para descoberta de dispositivos.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as udp_socket:
        udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

        discovery_request = DiscoveryMessage()
        discovery_request.device_type = "gateway"
        message = discovery_request.SerializeToString()

        udp_socket.sendto(message, (UDP_MULTICAST_GROUP, UDP_MULTICAST_PORT))
        print(f"[INFO] Solicitação de descoberta enviada para {UDP_MULTICAST_GROUP}:{UDP_MULTICAST_PORT}")

def handle_tcp_client(client_socket, address):
    """
    Lida com conexões TCP recebidas do cliente para enviar comandos aos dispositivos.
    """
    try:
        print(f"[INFO] Conexão TCP estabelecida com {address}")
        data = client_socket.recv(1024)

        # Processa a mensagem recebida
        request = DeviceRequest()
        request.ParseFromString(data)
        print(f"[INFO] Comando recebido: {request}")

        # Envia o comando ao dispositivo correspondente
        device = discovered_devices.get(request.id)
        if not device:
            raise ValueError("Dispositivo não encontrado.")

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as device_socket:
            device_socket.connect((device["ip"], device["port"]))
            device_socket.send(data)

            # Recebe a resposta do dispositivo
            response_data = device_socket.recv(1024)
            response = DeviceResponse()
            response.ParseFromString(response_data)
            print(f"[INFO] Resposta do dispositivo: {response}")

            # Envia a resposta de volta ao cliente
            client_socket.send(response_data)

    except (ValueError, DecodeError) as e:
        print(f"[ERRO] {e}")
        response = DeviceResponse(id=request.id if 'request' in locals() else -1, success=False, message=str(e))
        client_socket.send(response.SerializeToString())

    finally:
        client_socket.close()

def tcp_server():
    """
    Servidor TCP para se comunicar com o cliente.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("0.0.0.0", TCP_SERVER_PORT))
        server_socket.listen(5)
        print(f"[INFO] Servidor TCP aguardando conexões na porta {TCP_SERVER_PORT}")

        while True:
            client_socket, address = server_socket.accept()
            threading.Thread(target=handle_tcp_client, args=(client_socket, address)).start()

if __name__ == "__main__":
    # Descoberta de dispositivos
    threading.Thread(target=handle_udp_multicast, daemon=True).start()
    send_udp_multicast_request()

    # Servidor TCP
    threading.Thread(target=tcp_server, daemon=True).start()

    # Mantém o Gateway ativo
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[INFO] Gateway encerrado.")
