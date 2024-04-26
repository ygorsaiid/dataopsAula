"Script de ingestão e preparação - projeto dataops MBADE04"

import os
import uuid
from datetime import datetime
import logging
import requests
import pandas as pd
from dotenv import load_dotenv


from config import configs
import utils

config_file = configs
load_dotenv()
logging.basicConfig(level=logging.INFO)

def ingestion():
    """
    Função de ingestão dos dados
    Outputs: Salva base raw em local específico e retorna o nome do arquivo
    """

    logging.info("Iniciando a ingestão")
    api_url = os.getenv('URL')
    logging.info(api_url)

    try:
        response = requests.get(api_url, timeout=10).json()
        data = response['results']
    except requests.exceptions.RequestException as request_error:
        logging.error("Erro de solicitação HTTP: %s", request_error)
        utils.error_handler(request_error, 'read_api')
    except KeyError as key_error:
        logging.error("Erro de solicitação HTTP: %s", request_error)
        utils.error_handler(key_error, 'read_api')

    df = pd.json_normalize(data)
    df['load_date'] = datetime.now().strftime("%H:%M:%S")
    file = f"{config_file['raw_path']}{str(uuid.uuid4())}.csv"
    df.to_csv(file, sep=";", index=False)
    return file

def preparation(file):
    """
    Função de preparação dos dados: renomeia, tipagem, normaliza strings
    Arguments: file -> nome do arquivo raw
    Outputs: Salva base limpa em local específico
    """

    try:
        logging.info("Iniciando a preparação")
        df = pd.read_csv(file, sep=";")
        san = utils.Saneamento(df, config_file)
        san.select_rename()
        logging.info("Dados renomeados e selecionados")
        san.tipagem()
        logging.info("Dados tipados")
        san.trata_valores()
        logging.info("Caracteres tratados")
        san.save_work()
        logging.info("Dados salvos")
    except KeyError as key_error:
        logging.error("Erro : %s", key_error)
        utils.error_handler(key_error, 'read_api')


if __name__ == '__main__':
    file_name = ingestion()
    preparation(file_name)
