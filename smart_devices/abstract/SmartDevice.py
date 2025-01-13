import socket
import time
import struct
from abc import ABC, abstractmethod
from typing import Dict, Any
from smart_devices.proto.smart_devices_pb2 import smart_devices_pb2 as proto
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
    def process_command(self, command: str):
        """
        Método abstrato para processar comandos enviados ao dispositivo.
        """
        pass

    def info(self) -> Dict[str, Any]:
        return {
            "device_id": self._id,
            "device_name": self._name,
            "device_type": self._type,
            "is_on": self._is_on,
            "ip": self._ip,
            "port": self._port
        }

    def toggle_is_on(self) -> None:
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

    def start(self):
        """
        Inicia o dispositivo e envia periodicamente seu estado via socket multicast.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.ip))

        while True:
            try:
                message = self.to_proto().SerializeToString()
                logger.info(f"Enviando estado do dispositivo {self.id} para {MCAST_GROUP}:{MCAST_PORT}")
                sock.sendto(message, (MCAST_GROUP, MCAST_PORT))
            except Exception as e:
                logger.error(f"Erro ao enviar estado do dispositivo {self.id}: {e}")
            time.sleep(DISCOVERY_DELAY)

    def listen_for_commands(self):
        """
        Escuta e processa comandos recebidos via TCP.
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('0.0.0.0', self.port))
        server_socket.listen(5)
        logger.info(f"Dispositivo {self.name} está aguardando conexões TCP na porta {self.port}...")

        while True:
            try:
                client_socket, client_address = server_socket.accept()
                logger.info(f"Conexão recebida de {client_address}")

                # Receber e desserializar o comando
                data = client_socket.recv(1024)
                if data:
                    device_command = proto.DeviceCommand()
                    device_command.ParseFromString(data)

                    logger.info(f"Comando recebido: {device_command.command}")

                    # Processar o comando
                    response_message = self.process_command(device_command.command)

                    # Criar e enviar a resposta
                    command_response = proto.CommandResponse(message=response_message)
                    client_socket.sendall(command_response.SerializeToString())

                client_socket.close()
            except socket.error as e:
                logger.error(f"Erro de socket: {e}")
            except Exception as e:
                logger.error(f"Erro ao processar comando: {e}")

    def __str__(self):
        """
        Representação textual do dispositivo.
        """
        state_str = "ON" if self.is_on else "OFF"
        return f"SmartDevice(ID: {self._id}, Name: {self._name}, Type: {self._type}, State: {state_str}, IP: {self._ip}, Port: {self._port})"
