from View.TelaAlteracaoDados import AlteracaoDados
from View.PainelOpcao import PainelOpcao
from Controller import ConnectionDB
from Model.Enum.TipoTelaEnum import TipoTelaEnum
from Model import (Equipe,
                   Analista)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog


class CadastrarAnalista(QDialog):
    
    def __init__(self: object , db:ConnectionDB, tipo_cadastro: TipoTelaEnum, parent=None) -> None:
        super().__init__(parent)
        self.db: ConnectionDB = db
        self.parent = parent
        self.tipo_cadastro: TipoTelaEnum = tipo_cadastro
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setup_ui()
        if self.tipo_cadastro == TipoTelaEnum.CadastroUsuario:
            self.popular_combo_box()
        self.btn_events()

    def btn_events(self: object) -> None:
        self.btn_alterar_analista.clicked.connect(lambda: self.open_window(AlteracaoDados(self.db, self.tipo_cadastro, self.parent)))
        if self.tipo_cadastro == TipoTelaEnum.CadastroUsuario:
            self.btn_salvar.clicked.connect(self.salvar_analista)
        elif self.tipo_cadastro == TipoTelaEnum.CadastroEquipe:
            self.btn_salvar.clicked.connect(self.salvar_equipes)
        else:
            self.btn_salvar.clicked.connect(self.salvar_projetos)
            
    def popular_combo_box(self: object) -> None:
        equipes = tuple(map(lambda dado: Equipe(codigo=dado[0], nome=dado[1]), self.db.execute_procedure('SPC_EQUIPE', (1, 0))))
        self.box_equipe.addItem('Selecione') if self.box_equipe.findText('Selecione') == -1 else ''
        for equipe in equipes:
            if self.box_equipe.findText(equipe.nome) == -1:
                self.box_equipe.addItem(equipe.nome)
    
    def salvar_analista(self: object) -> None:
        cd_equipe = None
        equipes = tuple(map(lambda dado: Equipe(codigo=dado[0], nome=dado[1]), self.db.execute_procedure('SPC_EQUIPE', (1, 0))))
        equipe_analista = self.box_equipe.currentText()
        for equipe in equipes:
            if equipe_analista == equipe.nome:
                cd_equipe = equipe.codigo
                break
        if self.inpt_nome.text() == "" or self.inpt_email_analista.text() == "" or self.box_equipe.currentText() == "Selecione":
            self.open_window(PainelOpcao(TipoTelaEnum.DialogError,
                                         "Erro ao Cadastrar Analista.\nFalta de dados",
                                         self.parent))
        else:
            self.db.execute_procedure("SPI_ANALISTAS", (self.inpt_nome.text(), 
                                                    self.inpt_email_analista.text(),
                                                    cd_equipe))
            self.parent.atualizar_dados()
            self.close()

    def salvar_projetos(self: object) -> None:
        self.db.execute_procedure("SPI_PROJETO", (self.inpt_nome.text(), ))
        self.parent.atualizar_dados()
        self.close()
    
    def salvar_equipes(self: object) -> None:
        self.db.execute_procedure("SPI_EQUIPE", (self.inpt_nome.text(), ))
        self.parent.atualizar_dados()
        self.close()
    
    def open_window(self: object, tela:QtWidgets) -> None:
        tela_atual:QtWidgets = tela
        tela_atual.show()
        self.close()
        
    def setup_ui(self: object) -> None:
        self.setObjectName("cadastrar_analistas")
        self.setWindowIcon(QtGui.QIcon('Img/app_logo.png'))
        self.btn_salvar = QtWidgets.QPushButton(self)
        self.lbl_img = QtWidgets.QLabel(self)
        self.lbl_img.setGeometry(QtCore.QRect(130, 20, 171, 41))
        self.lbl_img.setText("")
        self.lbl_img.setPixmap(QtGui.QPixmap("Img\\logo.png"))
        self.lbl_img.setObjectName("lbl_img")
        if self.tipo_cadastro == TipoTelaEnum.CadastroUsuario :
            self.resize(512, 259)
            self.setMaximumSize(QtCore.QSize(512, 259))
            self.setModal(True)
            self.box_equipe = QtWidgets.QComboBox(self)
            self.box_equipe.setStyleSheet("color: #000; background-color: #fff;")
            self.box_equipe.setGeometry(QtCore.QRect(130, 170, 231, 31))
            font = QtGui.QFont()
            font.setFamily("Segoe UI Semibold")
            font.setPointSize(13)
            font.setItalic(False)
            self.box_equipe.setFont(font)
            self.box_equipe.setObjectName("box_equipe")
            self.lbl_equipe = QtWidgets.QLabel(self)
            self.lbl_equipe.setGeometry(QtCore.QRect(50, 170, 80, 31))
            font = QtGui.QFont()
            font.setFamily("Bahnschrift Light")
            font.setPointSize(16)
            font.setBold(True)
            font.setWeight(75)
            self.lbl_equipe.setFont(font)
            self.lbl_equipe.setObjectName("lbl_equipe")
            self.inpt_email_analista = QtWidgets.QLineEdit(self)
            self.inpt_email_analista.setGeometry(QtCore.QRect(130, 120, 250, 31))
            font = QtGui.QFont()
            font.setFamily("Segoe UI Semibold")
            font.setItalic(False)
            font.setPointSize(13)
            self.inpt_email_analista.setFont(font)
            self.inpt_email_analista.setObjectName("inpt_email_analista")
            self.inpt_email_analista.setStyleSheet("color: #000; background-color: #fff;")
            self.btn_salvar.setGeometry(QtCore.QRect(390, 210, 101, 31))
        else:
            self.resize(512, 192)
            self.setMaximumSize(QtCore.QSize(512, 192))
            self.setModal(True)
            self.btn_salvar.setGeometry(QtCore.QRect(210, 140, 101, 31))
        
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.btn_salvar.setFont(font)
        self.btn_salvar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_salvar.setStyleSheet("background-color: rgb(47, 79, 79);\n"
                                               "background-color: rgb(0, 62, 91);\n"
                                                "color: rgb(255, 255, 255);")
        self.btn_salvar.setObjectName("btn_salvar")
        self.lbl_inpt_nome = QtWidgets.QLabel(self)
        self.lbl_inpt_nome.setGeometry(QtCore.QRect(35, 70, 91, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_inpt_nome.setFont(font)
        self.lbl_inpt_nome.setObjectName("lbl_inpt_nome")
        self.btn_alterar_analista = QtWidgets.QPushButton(self)
        self.btn_alterar_analista.setGeometry(QtCore.QRect(430, 70, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.btn_alterar_analista.setFont(font)
        self.btn_alterar_analista.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_alterar_analista.setStyleSheet("color: rgb(255, 255, 255);\n"
                                                "background-color: rgb(0, 65, 0);")
        self.btn_alterar_analista.setObjectName("btn_alterar_analista")
        self.lbl_titulo_tela = QtWidgets.QLabel(self)
        self.lbl_titulo_tela.setGeometry(QtCore.QRect(170, 30, 250, 31))
        font = QtGui.QFont()
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_titulo_tela.setFont(font)
        self.lbl_titulo_tela.setStyleSheet("color: rgb(0, 24, 72);")
        self.lbl_titulo_tela.setObjectName("lbl_titulo_tela")
        self.inpt_nome = QtWidgets.QLineEdit(self)
        self.inpt_nome.setGeometry(QtCore.QRect(130, 70, 291, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        font.setItalic(False)
        self.inpt_nome.setFont(font)
        self.inpt_nome.setStyleSheet("color: #000; background-color: #fff;")
        self.inpt_nome.setObjectName("inpt_nome")
        self.lbl_email = QtWidgets.QLabel(self)
        self.lbl_email.setGeometry(QtCore.QRect(50, 120, 80, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.lbl_email.setFont(font)
        self.lbl_email.setObjectName("lbl_email")
        

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def AdquirirTitulo(self: object) -> str:
        if self.tipo_cadastro == TipoTelaEnum.CadastroUsuario :
            return "Analista"
        elif self.tipo_cadastro == TipoTelaEnum.CadastroEquipe :
            return "Equipe"
        return "Projeto"
    
    def retranslateUi(self: object) -> None:
        _translate = QtCore.QCoreApplication.translate
        
        self.lbl_titulo_tela.setText(_translate("cadastrar_analistas", f"Cadastro {self.AdquirirTitulo()}"))
        self.setWindowTitle(_translate("cadastrar_analistas", f"Cadastro {self.AdquirirTitulo()}"))
        self.btn_salvar.setText(_translate("cadastrar_analistas", "Salvar"))
        self.btn_alterar_analista.setText(_translate("cadastrar_analistas", "Alterar"))
        self.inpt_nome.setPlaceholderText(f"Insira o nome do(a) {self.AdquirirTitulo()}")
        if self.tipo_cadastro == TipoTelaEnum.CadastroUsuario :
            self.lbl_inpt_nome.setText(_translate("cadastrar_analistas", "Analista:"))
            self.lbl_equipe.setText(_translate("cadastrar_analistas", "Equipe:"))
            self.lbl_email.setText(_translate("cadastrar_analistas", "E-mail:"))
            self.inpt_email_analista.setPlaceholderText("Insira o E-mail")
            return
        if self.tipo_cadastro == TipoTelaEnum.CadastroEquipe :
            self.lbl_inpt_nome.setText(_translate("cadastrar_analistas", "Equipe:"))
            return
        self.lbl_inpt_nome.setText(_translate("cadastrar_analistas", "Projeto:"))