from Controller import ConnectionDB
from View import TelaPrincipal
from PyQt5.QtWidgets import QApplication
import sys
import json


class Main():
    
    def __init__(self: object) -> None:
        with open("appsettings.json", "r") as settings:
            app_config = json.load(settings)['AppConfig']
            db_info = app_config['db_server_prod'] if not bool(app_config['development_status']) else app_config['db_server_dev']
            self.db: ConnectionDB = ConnectionDB(host=db_info['Datasource'],
                                                 database=db_info['Database'],
                                                 user=db_info['DbUser']['UserId'],
                                                 password=db_info['DbUser']['Password'])
        self.tela_principal: TelaPrincipal = TelaPrincipal(self.db)
        self.tela_principal.show()
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = Main()
    app.exec_()
