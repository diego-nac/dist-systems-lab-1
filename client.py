import socket
import device_pb2  # Importando a definição do Protobuf

# Função para enviar comando para o gateway
def send_command(command):
    try:
        # Conectar-se ao gateway (presumindo que o gateway está rodando na porta 7000)
        gateway_ip = 'localhost'  # IP do gateway (substitua pelo IP correto)
        gateway_port = 7000  # Porta do gateway para comandos

        # Criar a mensagem de comando com Protobuf
        device_command = device_pb2.DeviceCommand()

        # Processar o comando
        if command.startswith("ligar"):
            parts = command.split()
            lamp_id = parts[1]
            device_command.command = "ligar"
            device_command.device_id = lamp_id
        elif command.startswith("desligar"):
            parts = command.split()
            lamp_id = parts[1]
            device_command.command = "desligar"
            device_command.device_id = lamp_id
        elif command.startswith("luminosidade"):
            parts = command.split()
            if len(parts) == 3 and parts[2].isdigit():
                device_command.command = "luminosidade"
                device_command.luminosity = int(parts[2])
                device_command.device_id = parts[1]
            else:
                print("Comando de luminosidade inválido. Use: 'luminosidade <id_da_lampada> <valor entre 0 e 100>'")
                return
        elif command == "listar dispositivos":
            device_command.command = "listar dispositivos"
            
        else:
            print("Comando inválido. Use 'ligar', 'desligar', 'luminosidade' ou 'listar dispositivos'.")
            return
        
        # Serializar a mensagem de comando
        message = device_command.SerializeToString()
        
        # Conectar ao gateway e enviar o comando
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((gateway_ip, gateway_port))
            client_socket.sendall(message)
            print(f"Comando '{command}' enviado ao gateway.")

            # Receber a resposta do gateway
            response = client_socket.recv(1024)
            command_response = device_pb2.CommandResponse()
            command_response.ParseFromString(response)
            print(f"Resposta do gateway: {command_response.message}")

    except Exception as e:
        print(f"Erro ao enviar comando ao gateway: {e}")

# Função principal para o cliente interagir com o gateway
def main():
    while True:
        # Solicita ao usuário que insira um comando
        command = input("Digite o comando (ex: ligar <id>, desligar <id>, luminosidade <id> <valor>, listar dispositivos): ")
        
        # Verifica se o comando é válido
        if command.strip().startswith("luminosidade"):
            try:
                # Verifica se o comando está no formato correto: "luminosidade <id> <valor>"
                parts = command.split()
                if len(parts) == 3 and parts[2].isdigit():
                    luminosity_value = int(parts[2])  # Valor da luminosidade
                    if 0 <= luminosity_value <= 100:
                        send_command(command)  # Envia o comando para o gateway
                    else:
                        print("Valor de luminosidade inválido. Use um valor entre 0 e 100.")
                else:
                    print("Comando inválido. Use: 'luminosidade <id_da_lampada> <valor entre 0 e 100>'")
            except Exception as e:
                print(f"Erro ao processar luminosidade: {e}")
        elif command.strip() == "listar dispositivos":
            send_command(command)  # Envia o comando de listar dispositivos
        elif command.strip():
            send_command(command)  # Envia o comando para o gateway
        else:
            print("Comando inválido. Tente novamente.")
            
        # Opcional: Se quiser sair do cliente de maneira controlada
        exit_command = input("Deseja enviar outro comando? (s/n): ")
        if exit_command.lower() == 'n':
            print("Saindo do cliente.")
            break

if __name__ == "__main__":
    main()
