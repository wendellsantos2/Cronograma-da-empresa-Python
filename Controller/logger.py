import os
import datetime


class Log():

    def __init__(self: object, *, diretorio: str,
                 nome_arquivo: str, modo_abertura: str):
        if not os.path.exists(diretorio):
            os.mkdir(diretorio)
        self.__diretorio = diretorio
        self.nome_arquivo = nome_arquivo
        self.modo_abertura = modo_abertura
        self.__localizacao_arquivo = os.path.join(self.__diretorio, nome_arquivo)
    
    def info(self, message: str) -> None:
        with open(self.__localizacao_arquivo, self.modo_abertura) as arq:
            arq.write(f"{datetime.datetime.now().strftime('%d/%m/%Y -%H:%M:%S')} {__name__} INFO --- {message}\n")
            
    def debug(self: object, message: str) -> None:
        with open(self.__localizacao_arquivo, self.modo_abertura) as arq:
            arq.write(f"{datetime.datetime.now().strftime('%d/%m/%Y -%H:%M:%S')} {__name__} DEBUG --- {message}\n")
    
    def critical(self: object, message: str) -> None:
        with open(self.__localizacao_arquivo, self.modo_abertura) as arq:
            arq.write(f"{datetime.datetime.now().strftime('%d/%m/%Y -%H:%M:%S')} {__name__} CRITICAL --- {message}\n")

    def error(self: object, message: str) -> None:
        with open(self.__localizacao_arquivo, self.modo_abertura) as arq:
            arq.write(f"{datetime.datetime.now().strftime('%d/%m/%Y -%H:%M:%S')} {__name__} [ERROR] --- {message}\n")
