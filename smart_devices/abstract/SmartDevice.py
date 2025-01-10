from abc import ABC, abstractmethod
from typing import Dict, Any
import socket
import time
import struct
from utils import *

class SmartDevice(ABC):
    """
    Classe abstrata para representar dispositivos inteligentes.
    Define a estrutura básica e métodos necessários para qualquer dispositivo inteligente.
    """

    def __init__(self, device_id: str, device_name: str, device_type: str, is_on: bool, device_ip: str, device_port: int):
        """
        Inicializa o dispositivo inteligente.

        :param device_id: ID único do dispositivo.
        :param device_name: Nome do dispositivo.
        :param device_type: Tipo do dispositivo (e.g., "Lamp", "AirConditioner").
        :param is_on: Estado inicial do dispositivo como um dicionário.
        :param device_ip: IP do dispositivo.
        :param device_port: Porta do dispositivo.
        """
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

        :param command: Um dicionário representando o comando.
        :return: Um dicionário com o resultado da execução do comando.
        """
        pass

    def info(self) -> Dict[str, Any]:
        """
        Retorna informações básicas sobre o dispositivo para descoberta.

        :return: Um dicionário com o ID, nome, tipo e estado inicial do dispositivo.
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
        Atualiza o estado do dispositivo.

        :param key: A chave do estado a ser atualizada.
        :param value: O novo valor do estado.
        """
        self._is_on = not self._is_on

    def start(self):
        """
        Método para iniciar o dispositivo e enviar periodicamente seu estado via socket multicast.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        group = socket.inet_aton(MCAST_GROUP)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        while True:
            message = self.__str__()
            logger.info(f".")
            sock.sendto(message.encode(), (MCAST_GROUP, MCAST_PORT))
            time.sleep(1)

    def __str__(self):
        """
        Representação textual do dispositivo.

        :return: Uma string representando o dispositivo.
        """
        return f"SmartDevice(ID: {self._id}, Name: {self._name}, Type: {self._type}, Is On: {self._is_on}, IP: {self._ip}, Port: {self._port})"
