import socket
import struct
import threading
import time
import random
import device_pb2  # Importando a definição do Protobuf

# Parâmetros de configuração do grupo de multicast
MCAST_GROUP = '224.0.0.1'  # Endereço multicast
MCAST_PORT = 5000          # Porta multicast
DEVICE_TYPE = 'lâmpada'    # Tipo do dispositivo

# Função para gerar um ID aleatório para o dispositivo
def generate_device_id():
    return f"lampada{random.randint(1000, 9999)}"  # Gerando um ID aleatório como 'lampada1234'

# Função para gerar um IP aleatório dentro do intervalo de IPs privados
def generate_device_ip():
    return f"127.0.1.{random.randint(0, 255)}"  # IP aleatório dentro de 127.0.1.x

# Estado inicial do dispositivo (pode ser 'ligado' ou 'desligado')
DEVICE_STATE = 'desligada'
LUMINOSITY = 0  # Luminosidade inicial (0-100)

# Função para enviar mensagens de descoberta via multicast
def send_discovery(device_id, device_ip):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)

        # Definir a porta da lâmpada para receber comandos
        device_port = 6000

        # Criar a mensagem de descoberta com Protobuf
        discovery_message = device_pb2.DeviceDiscovery(
            device_id=device_id,
            device_ip=device_ip,
            device_port=device_port,
            device_type="lampada",  # Tipo do dispositivo
            state=DEVICE_STATE,
            luminosity=LUMINOSITY
        )

        # Serializar a mensagem
        message = discovery_message.SerializeToString()
        sock.sendto(message, (MCAST_GROUP, MCAST_PORT))
        print(f"Mensagem de descoberta enviada: {discovery_message}")
        sock.close()
    except Exception as e:
        print(f"Erro ao enviar mensagem de descoberta: {e}")

def listen_for_commands(device_ip):
    global DEVICE_STATE, LUMINOSITY

    # Criar socket TCP para ouvir na porta configurada
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 6000))  # Escuta na porta 6000, em qualquer IP disponível
    server_socket.listen(5)
    print(f"A lâmpada {device_ip} está aguardando conexões TCP...")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Conexão recebida de {client_address}")

            # Receber o comando do gateway
            data = client_socket.recv(1024)
            if data:
                # Desserializar a mensagem recebida
                device_command = device_pb2.DeviceCommand()
                device_command.ParseFromString(data)

                print(f"Comando recebido: {device_command.command}")

                # Criar a resposta usando CommandResponse
                command_response = device_pb2.CommandResponse()

                # Alterar o estado da lâmpada ou luminosidade com base no comando
                if device_command.command == "ligar":
                    DEVICE_STATE = "ligada"
                    LUMINOSITY = 100  # Quando ligar, definir luminosidade para o máximo (100)
                    command_response.message = "Lâmpada ligada."
                    print(command_response.message)
                elif device_command.command == "desligar":
                    DEVICE_STATE = "desligada"
                    LUMINOSITY = 0  # Quando desligar, a luminosidade vai a 0
                    command_response.message = "Lâmpada desligada."
                    print(command_response.message)
                elif device_command.command == "luminosidade":
                    luminosity_level = device_command.luminosity
                    if 0 <= luminosity_level <= 100:
                        LUMINOSITY = luminosity_level
                        command_response.message = f"Luminosidade ajustada para {LUMINOSITY}%."
                        print(command_response.message)
                        if luminosity_level != 0:
                            DEVICE_STATE = "ligada"
                    else:
                        command_response.message = "Valor de luminosidade inválido. Use um valor entre 0 e 100."
                        print(command_response.message)
                else:
                    command_response.message = "Comando inválido."
                    print(command_response.message)

                # Serializar e enviar a resposta de volta ao gateway
                response_data = command_response.SerializeToString()
                client_socket.sendall(response_data)

            client_socket.close()
        except socket.error as e:
            print(f"Erro de socket: {e}")
        except Exception as e:
            print(f"Erro ao processar comando: {e}")
# Função para iniciar o envio de multicast e escutar comandos ao mesmo tempo
def start_lamp(device_id, device_ip):
    # Enviar mensagem de descoberta a cada 10 segundos
    while True:
        send_discovery(device_id, device_ip)
        time.sleep(10)  # Enviar a cada 10 segundos

# Função principal que inicia a lâmpada
def main():
    # Gerar um ID aleatório e um IP aleatório para a lâmpada
    device_id = generate_device_id()
    device_ip = generate_device_ip()

    # Iniciar o envio de mensagens de descoberta em uma thread
    threading.Thread(target=start_lamp, args=(device_id, device_ip), daemon=True).start()

    # Iniciar o escutador de comandos TCP em outra thread
    threading.Thread(target=listen_for_commands, args=(device_ip,), daemon=True).start()

    # Manter o programa rodando
    try:
        while True:
            time.sleep(1)  # Lâmpada continua executando
    except KeyboardInterrupt:
        print("\nLâmpada desligada.")

if __name__ == "__main__":
    main()
