
from Controller import ConnectionDB
from Model.Enum.TipoTelaEnum import TipoTelaEnum
from Model import (
                    Analista,
                    Equipe,
                    Projeto,
                    Modelo
                    )
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog


class AlteracaoDados(QDialog):
    
    def __init__(self:object, db: ConnectionDB, tipo_tela: TipoTelaEnum, parent=None) -> None:
        super().__init__(parent)
        self.db: ConnectionDB = db
        self.parent = parent
        self.tipo_tela = tipo_tela
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setup_ui()
        self.box_dados = (self.box_equipe, self.box_nome_excluir) if self.tipo_tela == TipoTelaEnum.CadastroUsuario else (self.box_nome_excluir)
        self.popular_box()
        self.btn_events()
    
    def btn_events(self: object) -> None:
        self.box_nome_excluir.currentTextChanged.connect(self.popular_inpts)
        self.btn_alterar_status.clicked.connect(self.alterar_status)
        self.btn_alterar.clicked.connect(self.alterar_dados)

    def popular_inpts(self: object) -> None:
        query = self.montar_query('select')
        if self.tipo_tela == TipoTelaEnum.CadastroUsuario:
            dados = tuple(map(lambda dado_generico: Analista(codigo=dado_generico[0], 
                                                             nome=dado_generico[1],
                                                             cd_status=dado_generico[2],
                                                             email=dado_generico[3],
                                                             id_equipe=dado_generico[4],
                                                             nome_equipe=dado_generico[5]
                                                             ),
                              self.db.execute_procedure(query, (None, 1))))
        else:
            dados = tuple(map(lambda dado_generico: Modelo(codigo=dado_generico[0],
                                                           nome=dado_generico[1], 
                                                           cd_status=dado_generico[2]), 
                                                           self.db.execute_procedure(query,
                                                                                    (None, 1))))
        dado_para_excluir = tuple(filter(lambda dado_generico:  self.box_nome_excluir.currentText() == dado_generico.nome, dados))[0]
        if dado_para_excluir.cd_status == 0:
            self.btn_alterar_status.setStyleSheet("background-color: rgb(51, 102, 153); color: rgb(255, 255, 255);")
            self.btn_alterar_status.setText("Ativar")
        else:
            self.btn_alterar_status.setStyleSheet("background-color: rgb(147, 31, 20);  color: rgb(255, 255, 255);")
            self.btn_alterar_status.setText("Desativar")
        self.inpt_novo_nome.setText(dado_para_excluir.nome)
        if self.tipo_tela == TipoTelaEnum.CadastroUsuario:
            self.inpt_email.setText(dado_para_excluir.email)
            self.box_equipe.setCurrentIndex(self.box_equipe.findText(dado_para_excluir.nome_equipe))
        
    def popular_box(self: object) -> None:
        self.box_nome_excluir.addItem("Selecione")
        dados = tuple(map(lambda modelo: Modelo(codigo=modelo[0], nome=modelo[1]), 
                          self.db.execute_procedure(self.montar_query('select'), (None, 1))))
        equipes = tuple(map(lambda dado: Equipe(codigo=dado[0], nome=dado[1]),
                            self.db.execute_procedure('SPC_EQUIPE', (None, 1) )))
        for dado in dados:
            if self.box_nome_excluir.findText(dado.nome) == -1:
               self.box_nome_excluir.addItem(dado.nome)
        if self.tipo_tela == TipoTelaEnum.CadastroUsuario:
            self.box_equipe.addItem("Selecione")
            for equipe in equipes:
                if self.box_equipe.findText(equipe.nome) == -1:
                    self.box_equipe.addItem(equipe.nome)
    
    def montar_query(self: object, tipo_query: str) -> str:
        if tipo_query == 'select':
            if self.tipo_tela == TipoTelaEnum.CadastroUsuario:
                return "SPC_ANALISTAS"
            elif self.tipo_tela == TipoTelaEnum.CadastroEquipe:
                return "SPC_EQUIPE"
            return  "SPC_PROJETO"
        
        if self.tipo_tela == TipoTelaEnum.CadastroUsuario:
                return "SPX_ANALISTAS"
        elif self.tipo_tela == TipoTelaEnum.CadastroEquipe:
            return "SPX_EQUIPE"
        return "SPX_PROJETO"
        
    def alterar_dados(self: object) -> None:
        procedure_principal = self.montar_query('select')
        if self.tipo_tela == TipoTelaEnum.CadastroUsuario:
            objeto = Analista
            equipes = tuple(map(lambda equipe: 
                Equipe(codigo=equipe[0], nome=equipe[1]),
                self.db.execute_procedure("SPC_EQUIPE", (None, 1))))
            
            dados = tuple(map(lambda dado: objeto(codigo=dado[0], 
                                                  nome=dado[1], 
                                                  email=dado[3],
                                                  nome_equipe=dado[5],
                                                  id_equipe=dado[4]
                                                  ), 
                              self.db.execute_procedure(procedure_principal, (None, 1))))
        else:
            objeto = Equipe if self.tipo_tela == TipoTelaEnum.CadastroEquipe else Projeto
            dados = tuple(map(lambda dado: objeto(codigo=dado[0], 
                                                  nome=dado[1]),
                                                  self.db.execute_procedure(procedure_principal, (None, 1))))
        nome_obj_excluir = self.box_nome_excluir.currentText()
        for dado in dados:
            if nome_obj_excluir == dado.nome:
                if self.tipo_tela == TipoTelaEnum.CadastroUsuario:
                    dados_procedure = dado.montar_query_update(self, equipes)
                    self.db.execute_procedure(dados_procedure[0], dados_procedure[1])
                else:
                    dados_procedure = dado.montar_query_update(self)
                    self.db.execute_procedure(dados_procedure[0], dados_procedure[1])
                break
        self.parent.atualizar_dados()
        self.close()
    
    def alterar_status(self: object) -> None:
        objetos = tuple(map(lambda objeto: Modelo(codigo=objeto[0],
                                                  nome=objeto[1],
                                                  cd_status=objeto[2]), 
                                            self.db.execute_procedure(
                                                self.montar_query('select'),
                                                (None, 1))))
        nome_objeto = self.box_nome_excluir.currentText()
        for objeto in objetos:
            if nome_objeto == objeto.nome:
                novo_cd_status = 1 if objeto.cd_status == 0 else 0
                self.db.execute_procedure(self.montar_query('update'), 
                                          (objeto.codigo, novo_cd_status))
                break
        self.close()
        self.parent.atualizar_dados()
        
    def adquirir_titulo(self: object) -> str:
        if self.tipo_tela == TipoTelaEnum.CadastroUsuario:
            return "Analista"
        elif self.tipo_tela == TipoTelaEnum.CadastroEquipe:
            return "Equipe"
        return "Projeto"
                
    def setup_ui(self):
        self.setObjectName("Alterar Dados")
        self.setWindowIcon(QtGui.QIcon('Img/app_logo.png'))
        self.resize(447, 325) if self.tipo_tela == TipoTelaEnum.CadastroUsuario else self.resize(447, 263)
        self.setMinimumSize(447, 325) if self.tipo_tela == TipoTelaEnum.CadastroUsuario else self.setMinimumSize(447, 263)
        self.setMaximumSize(447, 325) if self.tipo_tela == TipoTelaEnum.CadastroUsuario else self.setMaximumSize(447, 263)
        self.lbl_imagem = QtWidgets.QLabel(self)
        self.lbl_imagem.setGeometry(QtCore.QRect(90, 10, 41, 41))
        self.lbl_imagem.setPixmap(QtGui.QPixmap("Img\logo.png"))
        self.lbl_imagem.setObjectName("lbl_imagem")
        self.lbl_nome_excluir = QtWidgets.QLabel(self)
        self.lbl_nome_excluir.setGeometry(QtCore.QRect(40, 70, 100, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_nome_excluir.setFont(font)
        self.lbl_nome_excluir.setObjectName("lbl_nome_excluir")
        self.lbl_titulo = QtWidgets.QLabel(self)
        self.lbl_titulo.setGeometry(QtCore.QRect(140, 20, 240, 21))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_titulo.setFont(font)
        self.lbl_titulo.setStyleSheet("color: rgb(0, 34, 50);")
        self.lbl_titulo.setObjectName("lbl_titulo")
        self.box_nome_excluir = QtWidgets.QComboBox(self)
        self.box_nome_excluir.setGeometry(QtCore.QRect(140, 70, 241, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        self.box_nome_excluir.setFont(font)
        self.box_nome_excluir.setObjectName("box_nome_excluir")
        self.box_nome_excluir.setStyleSheet("color: #000; background-color: #fff")
        if self.tipo_tela == TipoTelaEnum.CadastroUsuario:
            self.lbl_equipe = QtWidgets.QLabel(self)
            self.lbl_equipe.setGeometry(QtCore.QRect(60, 180, 81, 31))
            font = QtGui.QFont()
            font.setFamily("Bahnschrift Light")
            font.setPointSize(16)
            font.setBold(True)
            font.setItalic(False)
            font.setWeight(75)
            self.lbl_equipe.setFont(font)
            self.lbl_equipe.setObjectName("lbl_equipe")
            self.box_equipe = QtWidgets.QComboBox(self)
            self.box_equipe.setStyleSheet("color: #000; background-color: #fff")
            self.box_equipe.setGeometry(QtCore.QRect(140, 180, 241, 31))
            font = QtGui.QFont()
            font.setFamily("Segoe UI Semibold")
            font.setPointSize(13)
            self.box_equipe.setFont(font)
            self.box_equipe.setObjectName("box_equipe")
            self.lbl_email = QtWidgets.QLabel(self)
            self.lbl_email.setGeometry(QtCore.QRect(60, 220, 81, 31))
            font = QtGui.QFont()
            font.setFamily("Bahnschrift Light")
            font.setPointSize(16)
            font.setBold(True)
            font.setItalic(False)
            font.setWeight(75)
            self.lbl_email.setFont(font)
            self.lbl_email.setObjectName("lbl_email")
            
            self.inpt_email = QtWidgets.QLineEdit(self)
            self.inpt_email.setGeometry(QtCore.QRect(140, 220, 241, 31))
            font = QtGui.QFont()
            font.setFamily("Segoe UI Semibold")
            font.setPointSize(13)
            self.inpt_email.setFont(font)
            self.inpt_email.setPlaceholderText("Insira o e-mail do Analista")
            self.inpt_email.setStyleSheet("color: #000; background-color: #fff")
            self.inpt_email.setObjectName("inpt_email")
            localizacao_btn_alterar =  QtCore.QRect(140, 260, 101, 31)
            btn_alterar_status = QtCore.QRect(280, 260, 101, 31)
        else:
            localizacao_btn_alterar =  QtCore.QRect(140, 200, 101, 31)
            btn_alterar_status = QtCore.QRect(280, 200, 101, 31)
        self.btn_alterar = QtWidgets.QPushButton(self)
        self.btn_alterar.setGeometry(localizacao_btn_alterar)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.btn_alterar.setFont(font)
        self.btn_alterar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_alterar.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(47, 79, 79);")
        self.btn_alterar.setObjectName("btn_alterar")

        self.btn_alterar_status = QtWidgets.QPushButton(self)
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        font.setBold(True)
        self.btn_alterar_status.setFont(font)
        self.btn_alterar_status.setGeometry(btn_alterar_status)
        self.btn_alterar_status.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_alterar_status.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(51, 102, 153);")
        self.btn_alterar_status.setObjectName("btn_alterar_status")
        
        self.inpt_novo_nome = QtWidgets.QLineEdit(self)
        self.inpt_novo_nome.setGeometry(QtCore.QRect(140, 140, 241, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        self.inpt_novo_nome.setFont(font)
        self.inpt_novo_nome.setPlaceholderText(f"Insira o novo nome")
        self.inpt_novo_nome.setStyleSheet("color: #000; background-color: #fff")
        self.inpt_novo_nome.setObjectName("inpt_novo_nome")
        self.lbl_nome = QtWidgets.QLabel(self)
        self.lbl_nome.setGeometry(QtCore.QRect(70, 140, 70, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_nome.setFont(font)
        self.lbl_nome.setObjectName("lbl_nome")
        self.line = QtWidgets.QFrame(self)
        self.line.setGeometry(QtCore.QRect(-3, 110, 511, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self: object) -> None:
        _translate = QtCore.QCoreApplication.translate
        if self.tipo_tela == TipoTelaEnum.CadastroUsuario:
            nome_lbl_excluir = "Analista:"
            self.lbl_equipe.setText(_translate("alterar_dados", "Equipe:"))
            self.lbl_email.setText(_translate("alterar_dados", "E-mail:"))
        elif self.tipo_tela == TipoTelaEnum.CadastroEquipe:
            nome_lbl_excluir = "Equipe:"
        else:
            nome_lbl_excluir = "Projeto:"
            
        self.setWindowTitle(_translate("alterar_dados", "Alterar Dados"))
        self.lbl_nome_excluir.setText(_translate("alterar_dados", nome_lbl_excluir))
        self.lbl_titulo.setText(_translate("alterar_dados", f"Alterar Dados {self.adquirir_titulo()}"))
        self.btn_alterar_status.setText(_translate("alterar_dados", "Ativar"))
        self.btn_alterar.setText(_translate("alterar_dados", "Alterar"))
        self.lbl_nome.setText(_translate("alterar_dados", "Nome:"))