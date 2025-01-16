import sys
import socket
import smart_devices.proto.smart_devices_pb2 as proto  # Importe o arquivo gerado pelo protoc

class Client:
    def __init__(self, gateway_ip="localhost", gateway_port=7000):
        """
        Inicializa o cliente que irá se comunicar com o gateway via TCP.
        :param gateway_ip: IP/Host onde o gateway está rodando.
        :param gateway_port: Porta na qual o gateway está escutando comandos.
        """
        self.gateway_ip = gateway_ip
        self.gateway_port = gateway_port
        print(f"Cliente inicializado para gateway em {gateway_ip}:{gateway_port}")

    def _send_device_command(self, device_command: proto.DeviceCommand) -> proto.CommandResponse:
        """
        Envia um DeviceCommand ao gateway e retorna um CommandResponse.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((self.gateway_ip, self.gateway_port))

                # Serializa a mensagem Protobuf
                msg_data = device_command.SerializeToString()

                # Envia ao gateway
                client_socket.sendall(msg_data)

                # Recebe a resposta do gateway
                response_data = client_socket.recv(1024)
                command_response = proto.CommandResponse()
                command_response.ParseFromString(response_data)

                return command_response

        except Exception as e:
            print(f"Erro ao enviar comando ao gateway: {e}")
            return proto.CommandResponse(success=False, message=str(e))

    def send_command(self, command: str, device_id: str = "", brightness: float = 0.0, color: str = "") -> None:
        """
        Monta a mensagem Protobuf `DeviceCommand` e envia ao gateway.
        """
        device_command = proto.DeviceCommand()
        device_command.command = command
        if device_id:
            device_command.device_id = device_id
        if brightness:
            device_command.brightness = brightness
        if color:
            device_command.color = color

        # Envia e obtém resposta
        command_response = self._send_device_command(device_command)

        # Exibe a resposta
        if command_response.success:
            print(f"Sucesso: {command_response.message}")
        else:
            print(f"Falha: {command_response.message}")

def main():
    client = Client(gateway_ip="localhost", gateway_port=7000)

    while True:
        print("\nSelecione uma opção:")
        print("1. Listar dispositivos")
        print("2. Ligar dispositivo")
        print("3. Desligar dispositivo")
        print("4. Ajustar luminosidade de uma lâmpada")
        print("5. Alterar cor de uma lâmpada")
        print("6. Sair")

        try:
            choice = int(input("Opção: "))
        except ValueError:
            print("Opção inválida! Digite um número de 1 a 6.")
            continue

        if choice == 1:
            client.send_command(command="listar dispositivos")

        elif choice == 2:
            device_id = input("Digite o ID do dispositivo a ser ligado: ").strip()
            client.send_command(command="ligar", device_id=device_id)

        elif choice == 3:
            device_id = input("Digite o ID do dispositivo a ser desligado: ").strip()
            client.send_command(command="desligar", device_id=device_id)

        elif choice == 4:
            device_id = input("Digite o ID da lâmpada: ").strip()
            try:
                brightness = float(input("Digite o nível de brightness (0 a 100): "))
                if 0 <= brightness <= 100:
                    client.send_command(command="brightness", device_id=device_id, brightness=brightness)
                else:
                    print("Valor de brightness inválido! Use um valor entre 0 e 100.")
            except ValueError:
                print("Valor de brightness inválido! Deve ser numérico.")

        elif choice == 5:
            device_id = input("Digite o ID da lâmpada: ").strip()
            color = input("Digite a cor desejada: ").strip()
            client.send_command(command="alterar cor", device_id=device_id, color=color)

        elif choice == 6:
            print("Encerrando cliente.")
            sys.exit(0)

        else:
            print("Opção inválida! Digite um número de 1 a 6.")

if __name__ == "__main__":
    main()