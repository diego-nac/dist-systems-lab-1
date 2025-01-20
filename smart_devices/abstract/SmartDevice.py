from threading import Thread
import time
from abc import ABC, abstractmethod
from typing import Dict, Any
import smart_devices.proto.smart_devices_pb2 as proto
from utils import *
import socket   

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
        self.tcp_connected = False

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
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(LOCAL_IP))
                    message = self.to_proto().SerializeToString()
                    logger.info(f"[Multicast] Enviando estado do dispositivo {self.id} para {MCAST_GROUP}:{MCAST_PORT}")
                    sock.sendto(message, (MCAST_GROUP, MCAST_PORT))
                time.sleep(DISCOVERY_DELAY)
            except Exception as e:
                logger.error(f"[Multicast] Erro ao enviar multicast: {e}")
                time.sleep(DISCOVERY_DELAY)

    def listen_for_commands(self):
        """
        Escuta e processa comandos recebidos via TCP.
        """
        try:
            logger.info(f"[TCP] Configurando socket na porta {self.port} e IP {self.ip}")
            
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((self.ip, self.port))  # Escutar no IP específico
            server_socket.listen(5)
            logger.info(f"[TCP] {self.name} aguardando conexões TCP no IP {self.ip}, porta {self.port}...")
            
            while True:
                try:
                    client_socket, client_address = server_socket.accept()
                    logger.info(f"[TCP] Conexão estabelecida com {client_address}")
                    data = client_socket.recv(1024)
                    
                    if data:
                        device_command = proto.DeviceCommand()
                        device_command.ParseFromString(data)
                        logger.info(f"[TCP] Comando recebido: {device_command.command}")

                        # Processa o comando
                        response_message = self.process_command(device_command)

                        # Envia resposta
                        command_response = proto.CommandResponse(
                            success=True if response_message else False,
                            message=response_message
                        )
                        client_socket.sendall(command_response.SerializeToString())

                except Exception as e:
                    logger.error(f"[TCP] Erro ao processar comando: {e}")
                finally:
                    client_socket.close()
        except Exception as e:
            logger.error(f"[TCP] Erro na configuração do servidor TCP: {e}")


    def start(self):
        """
        Inicia o dispositivo em duas threads:
        - Uma para enviar estado via multicast.
        - Outra para escutar comandos via TCP.
        """
        logger.info(f"Iniciando dispositivo {self.name} ({self.type})...")

        try:
            multicast_thread = Thread(target=self.start_multicast, daemon=True)
            tcp_listener_thread = Thread(target=self.listen_for_commands, daemon=True)

            multicast_thread.start()
            tcp_listener_thread.start()

            # Manter o processo ativo
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Dispositivo interrompido pelo usuário.")
        except Exception as e:
            logger.error(f"Erro ao iniciar threads do dispositivo: {e}")


    def __str__(self):
        """
        Representação textual do dispositivo.
        """
        state_str = "ON" if self.is_on else "OFF"
        return f"SmartDevice(ID: {self._id}, Name: {self._name}, Type: {self._type}, State: {state_str}, IP: {self._ip}, Port: {self._port})"
