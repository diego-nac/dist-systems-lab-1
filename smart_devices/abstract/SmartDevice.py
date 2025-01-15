from threading import Thread
import socket
import time
from abc import ABC, abstractmethod
from typing import Dict, Any
import smart_devices.proto.smart_devices_pb2 as proto
from utils import *

class SmartDevice(ABC):
    """
    Classe abstrata para representar dispositivos inteligentes.
    Define a estrutura básica e métodos necessários para qualquer dispositivo inteligente.
    """

    def __init__(self, device_id: str, device_name: str, device_type: str, is_on: bool, device_ip: str, device_port: int):
        self._id = device_id
        self._name = device_name
        self._type = device_type
        self._is_on = is_on
        self._ip = device_ip
        self._port = device_port
        self.tcp_connected = False  # Define se há uma conexão TCP ativa

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str):
        self._id = value

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def type(self) -> str:
        return self._type

    @type.setter
    def type(self, value: str):
        self._type = value

    @property
    def is_on(self) -> bool:
        return self._is_on

    @is_on.setter
    def is_on(self, value: bool):
        self._is_on = value

    @property
    def ip(self) -> str:
        return self._ip

    @ip.setter
    def ip(self, value: str):
        self._ip = value

    @property
    def port(self) -> int:
        return self._port

    @port.setter
    def port(self, value: int):
        self._port = value

    @abstractmethod
    def process_command(self, command: proto.DeviceCommand):
        """
        Método abstrato para processar comandos enviados ao dispositivo.
        """
        pass

    def info(self) -> Dict[str, Any]:
        """
        Retorna as informações básicas do dispositivo.
        """
        return {
            "device_id": self._id,
            "device_name": self._name,
            "device_type": self._type,
            "is_on": self._is_on,
            "ip": self._ip,
            "port": self._port
        }

    def toggle_is_on(self) -> None:
        """
        Alterna o estado de ligado/desligado do dispositivo.
        """
        self._is_on = not self._is_on

    def to_proto(self) -> proto.DeviceDiscovery:
        """
        Serializa o estado do dispositivo em uma mensagem Protobuf.
        """
        return proto.DeviceDiscovery(
            device_id=self.id,
            device_name=self.name,
            device_ip=self.ip,
            device_port=self.port,
            device_type=self.type,
            is_on=self.is_on
        )

    def start_multicast(self):
        """
        Envia periodicamente o estado do dispositivo via socket multicast.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(LOCAL_IP))

        while True:
            try:
                message = self.to_proto().SerializeToString()
                logger.info(f"Enviando estado do dispositivo {self.id} para {MCAST_GROUP}:{MCAST_PORT}")
                sock.sendto(message, (MCAST_GROUP, MCAST_PORT))
                time.sleep(DISCOVERY_DELAY)
            except Exception as e:
                logger.error(f"Erro ao enviar multicast: {e}")

    def listen_for_commands(self):
        """
        Escuta e processa comandos recebidos via TCP.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(5)
        logger.info(f"Dispositivo {self.name} aguardando conexões TCP na porta {self.port}...")

        while True:
            try:
                client_socket, client_address = server_socket.accept()
                self.tcp_connected = True  # Marca que há uma conexão TCP ativa
                logger.info(f"Conexão TCP estabelecida com {client_address}")

                data = client_socket.recv(1024)
                if data:
                    device_command = proto.DeviceCommand()
                    device_command.ParseFromString(data)
                    logger.info(f"Comando recebido: {device_command.command}")

                    response_message = self.process_command(device_command)

                    command_response = proto.CommandResponse(
                        success=True if "ON" in response_message or "OFF" in response_message else False,
                        message=response_message
                    )
                    client_socket.sendall(command_response.SerializeToString())

            except socket.error as e:
                logger.error(f"Erro de socket: {e}")
            except Exception as e:
                logger.error(f"Erro ao processar comando: {e}")
            finally:
                client_socket.close()

    def start(self):
        """
        Inicia o dispositivo em duas threads:
        - Uma para enviar estado via multicast.
        - Outra para escutar comandos via TCP.
        """
        logger.info(f"Iniciando dispositivo {self.name} ({self.type})...")
        multicast_thread = Thread(target=self.start_multicast, daemon=True)
        tcp_listener_thread = Thread(target=self.listen_for_commands, daemon=True)

        multicast_thread.start()
        tcp_listener_thread.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Dispositivo interrompido pelo usuário.")

    def __str__(self):
        """
        Representação textual do dispositivo.
        """
        state_str = "ON" if self.is_on else "OFF"
        return f"SmartDevice(ID: {self._id}, Name: {self._name}, Type: {self._type}, State: {state_str}, IP: {self._ip}, Port: {self._port})"
