"""Funções de tratamento dos dados"""
from datetime import datetime
import os
import re
import logging
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import mysql.connector


logging.basicConfig(level=logging.INFO)
load_dotenv()

class Saneamento:
    """
    Class Saneamento
    Outputs: Realiza o tratamento e limpeza dos dados
    """

    def __init__(self, data, configs):
        """
        Função init
        Outputs: configs
        """
        self.data = data
        self.metadado =  pd.read_excel(configs["meta_path"])
        self.len_cols = max(list(self.metadado["id"]))
        self.colunas = list(self.metadado['nome_original'])
        self.colunas_new = list(self.metadado['nome'])
        self.path_work = configs["work_path"]

    def select_rename(self):
        """
        Função select_rename
        Outputs: Renomeia colunas
        """
        self.data = self.data.loc[:, self.colunas]
        for i in range(self.len_cols):
            try:
                self.data.rename(columns={self.colunas[i]:self.colunas_new[i]}, inplace = True)
            except KeyError as e:
                print(f"Erro ao renomear coluna {self.colunas[i]: {e}}")

    def tipagem(self):
        """
        Função tipagem
        Outputs: Faz a tipagem das colunas
        """
        for col in self.colunas_new:
            tipo = self.metadado.loc[self.metadado['nome'] == col]['tipo'].item()
            if tipo == "int":
                tipo = self.data[col].astype(int)
            elif tipo == "float":
                self.data[col].replace(",", ".", regex=True, inplace = True)
                self.data[col] = self.data[col].astype(float)
            elif tipo == "date":
                self.data[col] = pd.to_datetime(self.data[col]).dt.strftime('%Y-%m-%d')

    def trata_valores(self):
        """
        Função remove caracteres especiais e transforma para lowercase
        Outputs: Remove os caracteres especiais de uma string
        """
        try:
            self.data = self.data.map(lambda x: x.lower() if isinstance(x, str) else x)
            self.data = self.data.map(
                lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', x) if isinstance(x, str) else x)
        except AttributeError as e:
            print(f"Erro de atributo: {e}")
            error_handler(e, "AttributeErrorCleanString")

    def save_work(self):
        """
        Função save_work
        Outputs: Salva as colunas e os dados já formatados para o sql
        """
        try:
            self.data['load_date'] = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

            user1 = os.getenv('MYSQL_USER')
            database1 = os.getenv('MYSQL_DATABASE')
            password1 = os.getenv('MYSQL_ROOT_PASSWORD')
            con = mysql.connector.connect(
                user=user1, password=password1, host='mysql', port="3306", database=database1)

            print("DB connected")

            engine  = create_engine(f"mysql+mysqlconnector://{user1}:{password1}@mysql/{database1}")
            self.data.to_sql('cadastro', con=engine, if_exists='append', index=False)
    
        except mysql.connector.Error as e:
            print(f"Erro de conexão com o banco de dados: {e}")
        finally:
            if con:
                con.close()

def error_handler(exception_error, stage):
    """
    Função error_handler
    Outputs: Trata erro
    """

    log = [stage, type(exception_error).__name__, exception_error,datetime.now()]
    logdf = pd.DataFrame(log).T

    if not os.path.exists("logs_file.txt"):
        logdf.columns = ['stage', 'type', 'error', 'datetime']
        logdf.to_csv("logs_file.txt", index=False,sep = ";")
    else:
        logdf.to_csv("logs_file.txt", index=False, mode='a', header=False, sep = ";")
