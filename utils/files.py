import json

from .LoggerConfig import LoggerConfig

logger = LoggerConfig("Files").get_logger()
def import_ips_from_json(file_path = 'data/devices_ips.json'):
    try:
        with open(file_path, 'r') as json_file:
            ips = json.load(json_file)
        logger.info(f"IPs importados do arquivo JSON: {ips}")
        return ips
    except FileNotFoundError:
        logger.error(f"Arquivo {file_path} não encontrado.")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar o arquivo JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Erro geral ao importar IPs do arquivo JSON: {e}")
        return []
