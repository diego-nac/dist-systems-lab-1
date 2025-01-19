from utils import *

DEVICE_IP = generate_device_ip(LOCAL_IP, offset=10)

class ConnectionManager:
    def __init__(
        self,
        device_ip=DEVICE_IP,
        device_port=DEVICES_PORT,
        multicast_group=MCAST_GROUP,
        multicast_port=MCAST_PORT,
        buffer_size=BUFFER_SIZE
    ):
        """
        Inicializa o gerenciador de conexões.
        - device_ip: IP do dispositivo que será usado para bind do servidor TCP.
        - device_port: Porta TCP para o servidor.
        - multicast_group: Endereço de grupo multicast para envio/recebimento.
        - multicast_port: Porta UDP para o multicast.
        - buffer_size: Tamanho do buffer para recebimento de dados.
        """
        self.local_ip = LOCAL_IP
        self.device_ip = device_ip 
        self.device_port = device_port
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.buffer_size = buffer_size


        logger.info(
            f"ConnectionManager inicializado.\n"
            f"IP local: {self.local_ip}\n"
            f"IP do dispositivo (TCP): {self.device_ip}\n"
            f"Multicast: {self.multicast_group}:{self.multicast_port}\n"
            f"Porta TCP: {self.device_port}"
        )
    def start_tcp_server(self, host=None, port=None, callback_function=None):
        if host is None:
            host = self.device_ip
        if port is None:
            port = self.device_port

        if host.startswith("224.") or host.startswith("239."):
            logger.error("O host fornecido é um endereço multicast, inválido para um servidor TCP.")
            return

        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                server_socket.bind((host, port))
            except OSError as e:
                logger.error(f"Erro ao associar o servidor ao endereço {host}:{port}: {e}")
                return
            
            logger.info(f"Servidor iniciado em {host}:{port}")
            server_socket.listen(5)
            logger.info("Aguardando conexões...")

            while True:
                client_socket, client_address = server_socket.accept()
                logger.info(f"Conexão recebida de {client_address}")
                try:
                    return_msg = callback_function(client_socket, client_address)
                    client_socket.sendall(return_msg)
                except Exception as e:
                    logger.error(f"Erro ao executar a função de callback para {client_address}: {e}")
                finally:
                    client_socket.close()
        except Exception as e:
            logger.error(f"Erro inesperado no servidor {host}:{port}: {e}")
        finally:
            try:
                server_socket.close()
                logger.info("Socket do servidor fechado.")
            except Exception as e:
                logger.error(f"Erro ao fechar o socket do servidor: {e}")
