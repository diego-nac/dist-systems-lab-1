import socket
import threading
import logging
import time
import struct

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_local_ip():
    """
    Retorna o IP local da máquina de forma simplificada.
    Exemplo: busca IP da interface padrão através de uma conexão 'dummy'.
    """
    try:
        # Faz uma conexão UDP "falsa" só para descobrir IP local
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except:
        return "127.0.0.1"

def generate_device_ip(local_ip, offset=10):
    """
    Exemplo fictício de geração de um IP de "dispositivo" baseado no IP local.
    Ajuste conforme sua lógica de negócio.
    """
    # Supondo que o IP seja algo como "192.168.0.100" e queremos offset = 10:
    # Poderíamos simplesmente transformar em int, somar 10 e voltar a string.
    # Aqui faremos algo mais simples como retornar o local_ip mesmo.
    return local_ip

class ConnectionManager:
    def __init__(
        self,
        device_ip=None,
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
        self.local_ip = get_local_ip()
        self.device_ip = device_ip or generate_device_ip(self.local_ip, offset=10)
        self.device_port = device_port
        self.multicast_group = multicast_group
        self.multicast_port = multicast_port
        self.buffer_size = buffer_size

        # Flags e estruturas para controle
        self._server_thread = None
        self._server_socket = None
        self._server_running = False

        self._multicast_thread = None
        self._multicast_socket = None
        self._multicast_running = False

        logger.info(
            f"ConnectionManager inicializado.\n"
            f"IP local: {self.local_ip}\n"
            f"IP do dispositivo (TCP): {self.device_ip}\n"
            f"Multicast: {self.multicast_group}:{self.multicast_port}\n"
            f"Porta TCP: {self.device_port}"
        )

    # -------------------------------------------------------------------------
    # Métodos para envio
    # -------------------------------------------------------------------------
    def send_unicast(self, target_ip, target_port, message):
        """
        Envia uma mensagem TCP (unicast) para um IP e porta específicos.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((target_ip, target_port))
                sock.sendall(message.encode("utf-8"))
                logger.info(f"[send_unicast] Mensagem enviada para {target_ip}:{target_port}: {message}")
        except Exception as e:
            logger.error(f"[send_unicast] Erro ao enviar para {target_ip}:{target_port}: {e}")

    def send_multicast(self, message):
        """
        Envia uma mensagem UDP para o grupo multicast configurado.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                # Define o TTL para 2 e a interface de saída (caso seja necessário)
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
                # Se quiser forçar a saída por um IP específico, descomente (e adapte):
                # sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self.device_ip))

                sock.sendto(message.encode("utf-8"), (self.multicast_group, self.multicast_port))
                logger.info(
                    f"[send_multicast] Mensagem enviada para {self.multicast_group}:{self.multicast_port}: {message}"
                )
        except Exception as e:
            logger.error(f"[send_multicast] Erro ao enviar multicast: {e}")

    # -------------------------------------------------------------------------
    # Métodos para servidor TCP (multi-thread)
    # -------------------------------------------------------------------------
    def start_tcp_server(self, bind_ip=None, bind_port=None, on_message_callback=None):
        """
        Inicia um servidor TCP em uma thread separada *e* bloqueia
        a chamada até que seja pressionado Ctrl+C.
        """
        if self._server_running:
            logger.warning("[start_tcp_server] Servidor TCP já está em execução.")
            return

        bind_ip = bind_ip or self.device_ip
        bind_port = bind_port or self.device_port
        on_message_callback = on_message_callback or self.default_on_message_callback

        # Seta a flag e sobe a thread de servidor
        self._server_running = True
        self._server_thread = threading.Thread(
            target=self._tcp_server_thread,   # método que faz o accept() e cria threads de cliente
            args=(bind_ip, bind_port, on_message_callback),
            daemon=True
        )
        self._server_thread.start()
        logger.info(f"[start_tcp_server] Servidor TCP iniciado em {bind_ip}:{bind_port}")

        # Aqui vem o "loop infinito" aguardando Ctrl+C
        try:
            logger.info("Servidor TCP ativo. Pressione Ctrl+C para encerrar.")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Recebido Ctrl+C. Encerrando servidor...")
            self.stop_tcp_server()
            logger.info("Servidor finalizado.")

    def _tcp_server_thread(self, bind_ip, bind_port, on_message_callback):
        """
        Thread que realiza o bind e aceita conexões. Para cada conexão,
        cria uma nova thread de atendimento ao cliente.
        """
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind((bind_ip, bind_port))
            self._server_socket.listen(5)
            logger.info(f"[TCP Server] Escutando em {bind_ip}:{bind_port} ...")

            while self._server_running:
                try:
                    client_socket, client_address = self._server_socket.accept()
                    logger.info(f"[TCP Server] Conexão recebida de {client_address}")

                    # Cria uma thread para lidar com o cliente
                    client_thread = threading.Thread(
                        target=self._handle_client_connection,
                        args=(client_socket, client_address, on_message_callback),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    pass
                except Exception as e:
                    logger.error(f"[TCP Server] Erro ao aceitar conexão: {e}")
                    time.sleep(1)

        except Exception as e:
            logger.error(f"[TCP Server] Erro no servidor TCP: {e}")
        finally:
            logger.info("[TCP Server] Encerrando servidor TCP.")

    def _handle_client_connection(self, client_socket, client_address, on_message_callback):
        """
        Trata cada conexão de cliente em uma thread dedicada.
        """
        with client_socket:
            try:
                while self._server_running:
                    data = client_socket.recv(self.buffer_size)
                    if not data:
                        break
                    message = data.decode("utf-8")
                    logger.info(f"[TCP Server] Mensagem recebida de {client_address}: {message}")

                    # Chama o callback de mensagem
                    on_message_callback(message, client_address)

                    # Opcional: envia um ACK de volta
                    client_socket.sendall(b"ACK")
            except Exception as e:
                logger.error(f"[TCP Server] Erro na conexão com {client_address}: {e}")
            finally:
                logger.info(f"[TCP Server] Conexão encerrada: {client_address}")

    def stop_tcp_server(self):
        """
        Encerra a execução do servidor TCP.
        """
        if not self._server_running:
            logger.warning("[stop_tcp_server] Servidor TCP não está em execução.")
            return

        self._server_running = False
        if self._server_socket:
            try:
                self._server_socket.close()
            except:
                pass
        logger.info("[stop_tcp_server] Servidor TCP foi sinalizado para parar.")

    # -------------------------------------------------------------------------
    # Métodos para recepção de multicast (multi-thread)
    # -------------------------------------------------------------------------
    def start_multicast_listener(self, on_message_callback=None):
        """
        Inicia a escuta de mensagens multicast em uma thread separada.
        - on_message_callback: função chamada ao receber uma mensagem UDP.
        """
        if self._multicast_running:
            logger.warning("[start_multicast_listener] Listener multicast já em execução.")
            return

        on_message_callback = on_message_callback or self.default_on_message_callback
        self._multicast_running = True
        self._multicast_thread = threading.Thread(
            target=self._multicast_listener_thread,
            args=(on_message_callback,),
            daemon=True
        )
        self._multicast_thread.start()
        logger.info(f"[start_multicast_listener] Escuta multicast iniciada em {self.multicast_group}:{self.multicast_port}")

    def _multicast_listener_thread(self, on_message_callback):
        """
        Thread que fica escutando o grupo multicast configurado,
        chamando o callback para cada mensagem recebida.
        """
        try:
            self._multicast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            self._multicast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._multicast_socket.bind(("", self.multicast_port))

            # Junta-se ao grupo multicast
            group = socket.inet_aton(self.multicast_group)
            mreq = struct.pack("4s4s", group, socket.inet_aton(self.local_ip))
            self._multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

            logger.info(f"[Multicast Listener] Escutando em {self.multicast_group}:{self.multicast_port}")

            while self._multicast_running:
                try:
                    data, addr = self._multicast_socket.recvfrom(self.buffer_size)
                    message = data.decode("utf-8")
                    logger.info(f"[Multicast Listener] Recebido de {addr}: {message}")

                    # Chama o callback de mensagem
                    on_message_callback(message, addr)
                except socket.timeout:
                    pass
                except Exception as e:
                    logger.error(f"[Multicast Listener] Erro ao receber dados: {e}")
                    time.sleep(1)

        except Exception as e:
            logger.error(f"[Multicast Listener] Erro no listener multicast: {e}")
        finally:
            logger.info("[Multicast Listener] Encerrando listener multicast.")

    def stop_multicast_listener(self):
        """
        Encerra a execução da thread de escuta multicast.
        """
        if not self._multicast_running:
            logger.warning("[stop_multicast_listener] Listener multicast não está em execução.")
            return

        self._multicast_running = False
        if self._multicast_socket:
            try:
                # Para deixar de escutar o grupo, podemos remover a associação também:
                group = socket.inet_aton(self.multicast_group)
                mreq = struct.pack("4s4s", group, socket.inet_aton(self.local_ip))
                self._multicast_socket.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, mreq)

                self._multicast_socket.close()
            except:
                pass
        logger.info("[stop_multicast_listener] Listener multicast foi sinalizado para parar.")

    # -------------------------------------------------------------------------
    # Callback padrão para mensagens
    # -------------------------------------------------------------------------
    def default_on_message_callback(self, message, address):
        """
        Callback padrão ao receber uma mensagem (tanto via TCP como UDP).
        """
        logger.info(f"[default_on_message_callback] Mensagem recebida de {address}: {message}")
