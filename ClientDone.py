import sys
import socket
import smart_devices.proto.smart_devices_pb2 as proto  # Importe o arquivo gerado pelo protoc (smart_devices.proto)
from utils import logger  # Supondo que seu 'utils' define logger

class Client:
    def __init__(self, gateway_ip="localhost", gateway_port=7000):
        """
        Inicializa o cliente que irá se comunicar com o gateway via TCP.
        :param gateway_ip: IP/Host onde o gateway está rodando.
        :param gateway_port: Porta na qual o gateway está escutando comandos.
        """
        self.gateway_ip = gateway_ip
        self.gateway_port = gateway_port
        logger.info(f"Cliente inicializado para gateway em {gateway_ip}:{gateway_port}")

    def _send_device_command(self, device_command: proto.DeviceCommand) -> proto.CommandResponse:
        """
        Envia um DeviceCommand ao gateway e retorna um CommandResponse.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                logger.info(f"Conectando ao gateway em {self.gateway_ip}:{self.gateway_port}")
                client_socket.connect((self.gateway_ip, self.gateway_port))

                # Serializa a mensagem Protobuf
                msg_data = device_command.SerializeToString()

                # Envia ao gateway
                client_socket.sendall(msg_data)
                logger.info(f"Comando '{device_command.command}' enviado ao gateway.")

                # Recebe a resposta do gateway
                response_data = client_socket.recv(1024)
                command_response = proto.CommandResponse()
                command_response.ParseFromString(response_data)

                logger.info(f"Recebida resposta do gateway: "
                            f"(success={command_response.success}) {command_response.message}")

                return command_response

        except Exception as e:
            logger.error(f"Erro ao enviar comando ao gateway: {e}", exc_info=True)
            # Em caso de erro, retorna uma resposta genérica de falha
            return proto.CommandResponse(success=False, message=str(e))

    def send_command(self, command: str, device_id: str = "", brightness: float = 0.0) -> None:
        """
        Monta a mensagem Protobuf `DeviceCommand` e envia ao gateway.
        Exemplo de uso:
          command="ligar", device_id="lamp_1", brightness=50.0
        """
        device_command = proto.DeviceCommand()
        device_command.command = command
        if device_id:
            device_command.device_id = device_id
        if command.lower() == "luminosidade":
            device_command.brightness = brightness

        # Envia e obtém resposta
        command_response = self._send_device_command(device_command)

        # Log da resposta
        if command_response.success:
            logger.info(f"Comando '{command}' executado com sucesso: {command_response.message}")
        else:
            logger.warning(f"Falha no comando '{command}': {command_response.message}")


def main():
    # Exemplo de inicialização do cliente
    client = Client(gateway_ip="localhost", gateway_port=7000)

    logger.info("Digite um comando. Exemplos:")
    logger.info("   ligar <id_dispositivo>")
    logger.info("   desligar <id_dispositivo>")
    logger.info("   luminosidade <id_dispositivo> <valor 0..100>")
    logger.info("   listar dispositivos")

    while True:
        command_line = input("\nComando> ").strip()
        if not command_line:
            logger.warning("Comando inválido, tente novamente.")
            continue

        parts = command_line.split()
        cmd = parts[0].lower()

        # Exemplo: "listar dispositivos"
        if cmd == "listar":
            if len(parts) == 2 and parts[1] == "dispositivos":
                client.send_command(command="listar dispositivos")
            else:
                logger.warning("Use: listar dispositivos")

        elif cmd in ["ligar", "desligar"]:
            # Ex: "ligar lamp_1"
            if len(parts) == 2:
                device_id = parts[1]
                client.send_command(command=cmd, device_id=device_id)
            else:
                logger.warning("Use: ligar <id> ou desligar <id>")

        elif cmd == "luminosidade":
            # Ex: "luminosidade lamp_1 50"
            if len(parts) == 3:
                device_id = parts[1]
                try:
                    luminosity_value = float(parts[2])
                    if 0 <= luminosity_value <= 100:
                        client.send_command(command="luminosidade", device_id=device_id, brightness=luminosity_value)
                    else:
                        logger.warning("Valor de luminosidade inválido. Use 0..100.")
                except ValueError:
                    logger.warning("Valor de luminosidade deve ser numérico.")
            else:
                logger.warning("Use: luminosidade <id> <valor 0..100>")

        elif cmd == "sair":
            logger.info("Encerrando cliente.")
            sys.exit(0)

        else:
            logger.warning(f"Comando '{cmd}' não reconhecido.")


if __name__ == "__main__":
    main()
