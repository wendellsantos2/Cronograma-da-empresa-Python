from Controller import ConnectionDB
from Model.Enum.TipoTelaEnum import TipoTelaEnum
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
import smtplib


class PainelOpcao(QDialog):
    
    def __init__(self, tipo_dialogo: TipoTelaEnum, descricao:str, parent=None):
        super().__init__(parent)
        self.tipo_dialogo = tipo_dialogo
        self.descricao = descricao
        if tipo_dialogo == TipoTelaEnum.DialogInfo:
            self.setup_dialog_info()
        elif tipo_dialogo == TipoTelaEnum.DialogError:
            self.setup_dialog_error()
        else:
            self.setup_dialog_warning()
        self.btn_events()
            
    def btn_events(self: object) -> None:
        self.btn_ok.clicked.connect(self.close)
    
    def setup_dialog_info(self: object) -> None:
        self.setObjectName("Informação")
        self.setWindowTitle("Informação")
        self.titulo = "Informação"
        self.setup_ui("Img\\informacao.png")
        
    def setup_dialog_warning(self: object) -> None:
        self.setObjectName("Aviso")
        self.setWindowTitle("Aviso")
        self.titulo = "Aviso"
        self.setup_ui("Img\\alerta.png")
    
    def setup_dialog_error(self: object) -> None:
        self.setObjectName("Erro")
        self.setWindowTitle("Erro")
        self.titulo = f"Error"
        self.setup_ui("Img\\img_error.png")
    
    def setup_ui(self: object, caminho_icon: str) -> None:
        self.resize(496, 164)
        self.setWindowIcon(QtGui.QIcon(caminho_icon))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.lbl_desc = QtWidgets.QLabel(self)
        self.lbl_desc.setGeometry(QtCore.QRect(0, 60, 496, 61))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lbl_desc.setFont(font)
        self.lbl_desc.setObjectName("lbl_desc")
        self.lbl_desc.setAlignment(QtCore.Qt.AlignCenter)
        self.line = QtWidgets.QFrame(self)
        self.line.setGeometry(QtCore.QRect(-3, 40, 500, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.lbl_titulo = QtWidgets.QLabel(self)
        localizacao_titulo = QtCore.QRect(205, 15, 250, 21) if self.tipo_dialogo != TipoTelaEnum.DialogError else QtCore.QRect(225, 15, 250, 21)
        self.lbl_titulo.setGeometry(localizacao_titulo)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lbl_titulo.setFont(font)
        self.lbl_titulo.setObjectName("lbl_titulo")
        
        self.pixmap_imagem = QtGui.QPixmap(caminho_icon)
        self.pixmap_imagem = self.pixmap_imagem.scaled(28, 28)
        
        self.lbl_imagem = QtWidgets.QLabel(self.centralwidget)
        self.lbl_imagem.setGeometry(QtCore.QRect(170, 10, 100, 100))
        self.lbl_imagem.setPixmap(self.pixmap_imagem)
        self.lbl_imagem.adjustSize()
        self.lbl_imagem.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.lbl_imagem.setObjectName("lbl_imagem")
        self.btn_ok = QtWidgets.QPushButton(self)
        self.btn_ok.setGeometry(QtCore.QRect(205, 130, 81, 23))
        self.btn_ok.setStyleSheet("border: 1px solid #333;\n"
"background-color: #8cb3d9;\n"
"color: #000;\n"
"font: 75 10pt \"MS Shell Dlg 2\";")
        self.btn_ok.setObjectName("btn_ok")
        self.btn_ok.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.lbl_desc.setText(_translate("self", self.descricao))
        # if self.tipo_dialogo
        self.lbl_titulo.setText(_translate("self", self.titulo))
        self.btn_ok.setText(_translate("self", "Ok"))

    