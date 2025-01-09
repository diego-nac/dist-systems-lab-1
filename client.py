import socket

# Função para enviar comando para o gateway
def send_command(command):
    try:
        # Conectar-se ao gateway (presumindo que o gateway está rodando na porta 7000)
        gateway_ip = 'localhost'  # IP do gateway (substitua pelo IP correto)
        gateway_port = 7000  # Porta do gateway para comandos

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((gateway_ip, gateway_port))

            # Enviar o comando ao gateway
            client_socket.sendall(command.encode())
            print(f"Comando '{command}' enviado ao gateway.")

            # Receber a resposta do gateway
            response = client_socket.recv(1024).decode()
            print(f"Resposta do gateway: {response}")
            
            # Opcional: Se quiser um feedback adicional de status do dispositivo, isso pode ser feito aqui
            # (Isso depende de como o gateway responde ou se o dispositivo enviar algo mais)
    except Exception as e:
        print(f"Erro ao enviar comando ao gateway: {e}")

# Função principal para o cliente interagir com o gateway
def main():
    while True:
        # Solicita ao usuário que insira um comando
        command = input("Digite o comando (ex: ligar <id>, desligar <id>, luminosidade <id> <valor>, ou listar dispositivos): ")
        
        # Verifica se o comando é válido
        if command.strip().startswith("luminosidade"):
            try:
                # Verifica se o comando está no formato correto: "luminosidade <id> <valor>"
                parts = command.split()
                if len(parts) == 3 and parts[2].isdigit():
                    lamp_id = parts[1]  # ID da lâmpada
                    luminosity_value = int(parts[2])  # Valor da luminosidade
                    

                    if 0 <= luminosity_value <= 100:
                        send_command(command)  # Envia o comando para o gateway
                    else:
                        print("Valor de luminosidade inválido. Use um valor entre 0 e 100.")
                else:
                    print("Comando inválido. Use: 'luminosidade <id_da_lampada> <valor entre 0 e 100>'")
            except Exception as e:
                print(f"Erro ao processar luminosidade: {e}")
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
