import socket
import struct
import threading
import time
import random

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

        # Mensagem de descoberta para o grupo multicast
        message = f"Dispositivo {device_id}, IP: {device_ip}, Porta: {device_port}, Estado: {DEVICE_STATE}, Luminosidade: {LUMINOSITY}"
        sock.sendto(message.encode('utf-8'), (MCAST_GROUP, MCAST_PORT))
        print(f"Mensagem de descoberta enviada: {message}")
        sock.close()
    except Exception as e:
        print(f"Erro ao enviar mensagem de descoberta: {e}")

# Função para ouvir conexões TCP e alterar o estado ou luminosidade da lâmpada
def listen_for_commands(device_ip):
    global DEVICE_STATE, LUMINOSITY

    # Criar socket TCP para ouvir na porta configurada
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Usar '0.0.0.0' para escutar em todas as interfaces de rede disponíveis
    server_socket.bind(('0.0.0.0', 6000))  # Escuta na porta 6000, em qualquer IP disponível
    server_socket.listen(5)
    print(f"A lâmpada {device_ip} está aguardando conexões TCP...")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            print(f"Conexão recebida de {client_address}")

            # Receber o comando do gateway
            command = client_socket.recv(1024).decode()
            if command:
                print(f"Comando recebido: {command}")

                # Alterar o estado da lâmpada ou luminosidade com base no comando
                if command == "ligar":
                    DEVICE_STATE = "ligada"
                    LUMINOSITY = 100  # Quando ligar, definir luminosidade para o máximo (100)
                    print("Lâmpada ligada.")
                    client_socket.sendall("Lâmpada ligada.".encode())
                elif command == "desligar":
                    DEVICE_STATE = "desligada"
                    LUMINOSITY = 0  # Quando desligar, a luminosidade vai a 0
                    print("Lâmpada desligada.")
                    client_socket.sendall("Lâmpada desligada.".encode())
                elif command.startswith("luminosidade"):
                    try:
                        luminosity_level = int(command.split()[1])
                        if 0 <= luminosity_level <= 100:
                            LUMINOSITY = luminosity_level
                            print(f"Luminosidade ajustada para {LUMINOSITY}%.")
                            client_socket.sendall(f"Luminosidade ajustada para {LUMINOSITY}%.".encode())
                            if(luminosity_level != 0):
                                DEVICE_STATE = "ligada"
                        else:
                            client_socket.sendall("Valor de luminosidade inválido. Use um valor entre 0 e 100.".encode())
                    except ValueError:
                        client_socket.sendall("Comando inválido. Use: 'luminosidade <valor entre 0 e 100>'.".encode())
                else:
                    client_socket.sendall("Comando inválido.".encode())
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
