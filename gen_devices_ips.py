import json
from utils.ips import generate_valid_ips
from utils import logger

def generate_ips_to_json(file_path, count):
    try:
        ips = generate_valid_ips(count)
        if not ips:
            raise ValueError("Não foi possível gerar IPs válidos.")

        with open(file_path, 'w') as json_file:
            json.dump(ips, json_file)
        logger.info(f"Arquivo JSON com IPs gerados salvo em: {file_path}")
    except Exception as e:
        logger.error(f"Erro ao gerar o arquivo JSON: {e}")

if __name__ == '__main__':
    generate_ips_to_json("data/devices_ips.json", 5)