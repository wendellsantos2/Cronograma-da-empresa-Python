from doctest import Example
from typing import Literal
import mysql.connector

class ConnectionDB:
    def __init__(self:object, user: str, host:str, password: str, database: str) -> None:
        self.user = user
        self.host = host
        self.password = password
        self.database = database

    def execute_query(self:object, query: str) -> Literal["str", "dados"]:
        cnx = self.conexao_db()
        try:
            cursor = cnx.cursor()
            cursor.execute(query)
            if "select" in query.lower():
                val = cursor.fetchall()
                if len(val) > 0:
                    cnx.close()
                    return val
            return
        except Exception as error:
            print(f"[Erro] {error}")

    def execute_procedure(self:object, proc_name: str, argumentos: tuple = None) -> Literal["str", "tuple"]:
        cnx = self.conexao_db()
        try:
            cursor = cnx.cursor()
            if argumentos is not None:
                cursor.callproc(proc_name, argumentos)
            else:
                cursor.callproc(proc_name)
            if "SPC" in proc_name:    
                for results in cursor.stored_results():
                    val = results.fetchall()
                if len(val) > 0:
                    cnx.close()
                    return val
            return
        except Exception as error:
            print(f"[Erro] {error}")
    
    def conexao_db(self) -> mysql.connector.connect:
        try:
            cnx = mysql.connector.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.database,
                autocommit=True
            )
            return cnx
        except Exception as error:
            print(error)
