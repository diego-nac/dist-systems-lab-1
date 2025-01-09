import socket
import threading
import time
from google.protobuf.message import DecodeError
from device_pb2 import DiscoveryMessage, DeviceRequest, DeviceResponse

DEVICE_TYPE = "lampada"
DEVICE_ID = 2
UDP_MULTICAST_GROUP = "239.255.255.250"
UDP_MULTICAST_PORT = 12345
TCP_SERVER_PORT = 54322

STATE = {
    "active": False,
    "intensity": 0
}

def send_multicast_discovery():
    discovery_message = DiscoveryMessage()
    discovery_message.device_type = DEVICE_TYPE
    discovery_message.id = DEVICE_ID
    discovery_message.ip = socket.gethostbyname(socket.gethostname())
    discovery_message.port = TCP_SERVER_PORT
    discovery_message.active = STATE["active"]

    message = discovery_message.SerializeToString()

    # socket multicast
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as udp_socket:
        udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        udp_socket.sendto(message, (UDP_MULTICAST_GROUP, UDP_MULTICAST_PORT))
        print(f"[INFO] Mensagem de descoberta enviada: {discovery_message}")

def handle_tcp_connection(client_socket, address):
    try:
        print(f"[INFO] Conexao TCP estabelecida com {address}")
        data = client_socket.recv(1024)

        request = DeviceRequest()
        request.ParseFromString(data)
        print(f"[INFO] Comando recebido: {request}")

        if request.command == "ligar":
            STATE["active"] = True
        elif request.command == "desligar":
            STATE["active"] = False
        elif request.command == "ajustar":
            intensity = int(request.parameters.get("intensity", STATE["intensity"]))
            STATE["intensity"] = max(0, min(100, intensity))

        response = DeviceResponse()
        response.id = DEVICE_ID
        response.success = True
        response.message = f"Estado atualizado: {STATE}"
        client_socket.send(response.SerializeToString())
        print(f"[INFO] Resposta enviada: {response}")

    except DecodeError as e:
        print(f"[ERRO] Falha ao decodificar mensagem: {e}")
    finally:
        client_socket.close()

def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("0.0.0.0", TCP_SERVER_PORT))
        server_socket.listen(5)
        print(f"[INFO] Servidor TCP aguardando conexões na porta {TCP_SERVER_PORT}")

        while True:
            client_socket, address = server_socket.accept()
            threading.Thread(target=handle_tcp_connection, args=(client_socket, address)).start()

def periodic_state_report():
    while True:
        time.sleep(15)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
            state_message = DiscoveryMessage()
            state_message.device_type = DEVICE_TYPE
            state_message.id = DEVICE_ID
            state_message.ip = socket.gethostbyname(socket.gethostname())
            state_message.port = TCP_SERVER_PORT
            state_message.active = STATE["active"]

            udp_socket.sendto(state_message.SerializeToString(), (UDP_MULTICAST_GROUP, UDP_MULTICAST_PORT))
            print(f"[INFO] Estado atual enviado: {STATE}")

if __name__ == "__main__":
    send_multicast_discovery()

    # TCP e envio periódico
    threading.Thread(target=tcp_server, daemon=True).start()
    threading.Thread(target=periodic_state_report, daemon=True).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Dispositivo encerrado.")
