from Controller import ConnectionDB
from Model.Enum.TipoTelaEnum import TipoTelaEnum
from Model.Enum.TipoProgramacaoEnum import TipoProgramacaoEnum
from Model import (Equipe,
                   Analista, 
                   Categoria, 
                   Projeto)
from View.CadastrarAnalista import CadastrarAnalista
from View.PainelOpcao import PainelOpcao
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow
from View.ListagemViagem import ListagemViagem
import ctypes
import datetime, calendar


class TelaPrincipal(QMainWindow):
    
    def __init__(self:object, db:ConnectionDB, parent=None) -> None:
        super().__init__(parent)        
        self.db = db
        self.setup_ui()
        # A ordem à ser seguida é sempre a ordem dessa lista
        self.box_dados = (self.box_categoria, self.box_analist,
        self.box_equipe, self.box_projeto)
        self.popular_tela()
        self.btn_events()
    
    def popular_tela(self):
        categorias = tuple(map(lambda categoria: Categoria(categoria[0],
                                                           categoria[1]), 
                               self.db.execute_procedure('SPC_CATEGORIA', None)))
        analistas = tuple(map(lambda analista: Analista(codigo=analista[0],
                                                        nome=analista[1],
                                                        id_equipe=analista[4]),
                              self.db.execute_procedure('SPC_ANALISTAS', (1, 0))))
        equipes = tuple(map(lambda equipe: Equipe(equipe[0],
                                                  equipe[1]),
                            self.db.execute_procedure('SPC_EQUIPE', (1, 0))))
        
        projetos = tuple(map(lambda projeto: Projeto(projeto[0], 
                                                     projeto[1]),
                             self.db.execute_procedure('SPC_PROJETO', (1, 0))))
        self.dados = [categorias, analistas, equipes, projetos]
        for x in self.box_dados:
            x.clear()    
            x.addItem('Selecione')
        
        for indice in range(len(self.dados)):
            for indice2 in range(len(self.dados[indice])):
                if type(self.dados[indice]) is Analista:
                    self.box_dados[indice].addItem(self.dados[indice][indice2].nome)
                else:
                    self.box_dados[indice].addItem(self.dados[indice][indice2].nome)
                
    def alterar_data_fim(self: object) -> None:
        data_inicio = datetime.datetime.strptime(self.inpt_data_inicio.text(), '%d/%m/%Y')
        data_fim = datetime.datetime.strptime(self.inpt_data_fim.text(), '%d/%m/%Y')
        if data_inicio.month != data_fim.month or data_inicio.year != data_fim.year:
            self.inpt_data_fim.setDateTime(QtCore.QDateTime(datetime.datetime(
                day=calendar.monthrange(data_inicio.year,
                                        data_inicio.month)[1], 
                month=data_inicio.month,
                year=data_inicio.year), QtCore.QTime(0, 0, 0)))
        
    def btn_events(self: object) -> None:
        self.inpt_data_inicio.dateTimeChanged.connect(self.alterar_data_fim)
        self.box_analist.currentTextChanged.connect(self.pegar_equipe_analista)
        self.btn_cadastrar_analista.clicked.connect(lambda: self.open_window(CadastrarAnalista(self.db,
                                                                                               TipoTelaEnum.CadastroUsuario, 
                                                                                               self)))
        self.btn_consultar_viagem.clicked.connect(lambda: self.open_window(ListagemViagem(self.db,
                                                                                          TipoProgramacaoEnum.Viagem,
                                                                                          self)))
        self.btn_cadastrar_projeto.clicked.connect(lambda: self.open_window(CadastrarAnalista(self.db, 
                                                                                              TipoTelaEnum.CadastroEquipe,
                                                                                              self)))
        self.btn_cadastrar_equipe.clicked.connect(lambda: self.open_window(CadastrarAnalista(self.db,
                                                                                             TipoTelaEnum.CadastroProjeto, 
                                                                                             self)))
        self.btn_consultar_plantao.clicked.connect(lambda: self.open_window(ListagemViagem(self.db,
                                                                                           TipoProgramacaoEnum.Plantao,
                                                                                           self)))
        self.btn_salvar_agenda.clicked.connect(self.salvar_dados)
        self.btn_cancelar_agenda.clicked.connect(self.atualizar_dados)
        
    def pegar_equipe_analista(self: object) -> None:
        analistas = tuple(map(lambda analista: Analista(codigo=analista[0],
                                                        nome=analista[1],
                                                        nome_equipe=analista[5]),
                              self.db.execute_procedure('SPC_ANALISTAS', (1, 0))))
        for dado in analistas:
            if dado.nome == self.box_analist.currentText():
                self.box_equipe.setCurrentIndex(self.box_equipe.findText(dado.nome_equipe))
                break
            
    def salvar_dados(self: object) -> None:
        dadosUtilizados = []
        self.lbl_falha.setHidden(True)
        categorias = tuple(map(lambda categoria: Categoria(categoria[0],
                                                           categoria[1]), 
                               self.db.execute_procedure('SPC_CATEGORIA', None)))
        analistas = tuple(map(lambda analista: Analista(codigo=analista[0],
                                                        id_equipe=analista[4],
                                                        nome=analista[1]),
                              self.db.execute_procedure('SPC_ANALISTAS', (1, 0))))
        equipes = tuple(map(lambda equipe: Equipe(equipe[0],
                                                  equipe[1]),
                            self.db.execute_procedure('SPC_EQUIPE', (1, 0))))
        
        projetos = tuple(map(lambda projeto: Projeto(projeto[0], 
                                                     projeto[1]),
                             self.db.execute_procedure('SPC_PROJETO', (1, 0))))
        
        self.dados = (categorias, analistas, equipes, projetos)
        listaDados = tuple(map(lambda x: x.currentText(), self.box_dados))

        for indiceLista1 in range(len(self.dados)):
            for indiceLista2 in range(len(self.dados[indiceLista1])):
                if listaDados[indiceLista1] == self.dados[indiceLista1][indiceLista2].nome:
                    dadosUtilizados.append(self.dados[indiceLista1][indiceLista2].codigo)
        
        data_inicio = self.inpt_data_inicio.text()  
        data_inicio = datetime.datetime(int(data_inicio.split('/')[2]),
                                        int(data_inicio.split('/')[1]),
                                        int(data_inicio.split('/')[0])).strftime('%Y-%m-%d')
        data_fim = self.inpt_data_fim.text()
        data_fim = datetime.datetime(int(data_fim.split('/')[2]),
                                     int(data_fim.split('/')[1]),
                                     int(data_fim.split('/')[0])).strftime('%Y-%m-%d')

        if len(dadosUtilizados) < 4:
            self.open_window(PainelOpcao(TipoTelaEnum.DialogError,
                                         "Falta de dados",
                                         self))
            for box in self.box_dados:
                if box.currentText() == "Selecione":
                    box.setStyleSheet("background-color: rgb(255, 255, 255);border: 1px solid rgb(255,0, 0);")
                else:
                    box.setStyleSheet("background-color: rgb(255, 255, 255);")
            return
        tipo_insercao = 0 if dadosUtilizados[0] == 2 else 1
        self.db.execute_procedure("SPI_VIAGEM_PLANTAO", 
                                  (tipo_insercao,
                                   str(dadosUtilizados[1]),
                                   str(dadosUtilizados[0]),
                                   str(dadosUtilizados[2]),
                                   str(dadosUtilizados[3]),
                                   data_inicio,
                                   data_fim))
        for  b in self.box_dados:
            b.setCurrentIndex(0)
        # Ver nova forma de atualizar itens
        self.atualizar_dados()

    def atualizar_dados(self: object) -> None:
        self.lbl_falha.setHidden(True)
        tuple(map(lambda dado: dado.clear(), self.box_dados))
        tuple(map(lambda dado: dado.addItem("Selecione"), self.box_dados))
        categorias = tuple(map(lambda categoria: Categoria(codigo=categoria[0],
                                                           nome=categoria[1]), 
                               self.db.execute_procedure('SPC_CATEGORIA', None)))
        analistas = tuple(map(lambda analista: Analista(codigo=analista[0],
                                                        nome=analista[1],
                                                        id_equipe=analista[4]
                                                        ),
                              self.db.execute_procedure('SPC_ANALISTAS', (1, 0))))
        equipes = tuple(map(lambda equipe: Equipe(codigo=equipe[0],
                                                  nome=equipe[1]),
                            self.db.execute_procedure('SPC_EQUIPE', (1, 0))))
        
        projetos = tuple(map(lambda projeto: Projeto(codigo=projeto[0], 
                                                     nome=projeto[1]),
                             self.db.execute_procedure('SPC_PROJETO', (1, 0))))
        self.dados = (categorias, analistas, equipes, projetos)
        map(lambda dado: dado.clear, self.box_dados)
        for indice in range(len(self.dados)):
            self.box_dados[indice].setStyleSheet("background-color: rgb(255, 255, 255);")
            for indice2 in range(len(self.dados[indice])):
                if type(self.dados[indice]) is Analista:
                    self.box_dados[indice].addItem(self.dados[indice][indice2].nome)
                else:
                    self.box_dados[indice].addItem(self.dados[indice][indice2].nome)
    
    def open_window(self: object, tela:QtWidgets) -> None:
        tela_atual:QtWidgets = tela
        tela_atual.show()
        
    def setup_ui(self: object) -> None:
        user32 = ctypes.windll.user32
        ajuste_fonte = 0
        tamanho_tela_x, tamanho_tela_y = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        tamanhos_tela_padrao = [[1280, 720], [1920, 1080], [ 2560, 1440]]
        if tamanho_tela_x >= 1280 and tamanho_tela_x < 1366 and tamanho_tela_y >= 720 and tamanho_tela_y < 768:
            ajuste_fonte = 4
        elif tamanho_tela_x >= 1366 and tamanho_tela_x < 1920 and tamanho_tela_y >= 768 and tamanho_tela_y < 1080:
            ajuste_fonte = 2 
            
        css_inpt_objects = "background-color: rgb(255, 255, 255);\n"\
                           "color: #333333;"
        css_btn_objects = "background-color: rgb(113, 113, 85);\n"\
                          "color: rgb(255, 255, 255);"
                          
        self.setObjectName("Tela Principal")
        self.resize(612, 521)
        self.setWindowIcon(QtGui.QIcon('Img/app_logo.png'))
        self.setMinimumSize(QtCore.QSize(612, 521))
        self.setMaximumSize(QtCore.QSize(612, 521))
        self.setStyleSheet("background-color: rgb(192, 192, 192);")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.lbl_autores = QtWidgets.QLabel(self.centralwidget)
        self.lbl_autores.setGeometry(QtCore.QRect(10, 460, 300, 50))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPixelSize((10 - ajuste_fonte))
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_autores.setFont(font)
        self.lbl_autores.setObjectName("lbl_autores")
        
        
        self.lbl_analista = QtWidgets.QLabel(self.centralwidget)
        self.lbl_analista.setGeometry(QtCore.QRect(60, 120, 91, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_analista.setFont(font)
        self.lbl_analista.setObjectName("lbl_analista")

        self.lbl_data_inicio = QtWidgets.QLabel(self.centralwidget)
        self.lbl_data_inicio.setGeometry(QtCore.QRect(30, 240, 121, 31))
        
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_data_inicio.setFont(font)
        self.lbl_data_inicio.setObjectName("lbl_data_inicio")
        self.lbl_data_fim = QtWidgets.QLabel(self.centralwidget)
        self.lbl_data_fim.setGeometry(QtCore.QRect(310, 240, 41, 31))
        
        self.inpt_data_inicio = QtWidgets.QDateEdit(self.centralwidget)
        self.inpt_data_inicio.setGeometry(QtCore.QRect(160, 240, 131, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        self.inpt_data_inicio.setFont(font)
        self.inpt_data_inicio.setStyleSheet(css_inpt_objects)
        self.inpt_data_inicio.setAlignment(QtCore.Qt.AlignCenter)
        ano = datetime.datetime.now().year
        mes = datetime.datetime.now().month
        self.inpt_data_inicio.setDateTime(QtCore.QDateTime(datetime.datetime(day=datetime.datetime.now().day, month=mes, year=ano), QtCore.QTime(0, 0, 0)))
        self.inpt_data_inicio.setObjectName("inpt_data_inicio")
        
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_data_fim.setFont(font)
        self.lbl_data_fim.setObjectName("lbl_data_fim")
                
        self.inpt_data_fim = QtWidgets.QDateEdit(self.centralwidget)
        self.inpt_data_fim.setGeometry(QtCore.QRect(360, 240, 131, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        self.inpt_data_fim.setFont(font)
        self.inpt_data_fim.setStyleSheet(css_inpt_objects)
        self.inpt_data_fim.setAlignment(QtCore.Qt.AlignCenter)
        
        self.inpt_data_fim.setDateTime(QtCore.QDateTime(datetime.datetime(day=calendar.monthrange(ano, mes)[1], month=mes, year=ano), QtCore.QTime(0, 0, 0)))
        # self.inpt_data_fim.setMaximumDateTime(QtCore.QDateTime(QtCore.QDate(2022, 12, 31), QtCore.QTime(23, 59, 59)))
        self.inpt_data_fim.setObjectName("lbl_data_fim")

        self.box_projeto = QtWidgets.QComboBox(self.centralwidget)
        self.box_projeto.setGeometry(QtCore.QRect(160, 290, 221, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        self.box_projeto.setFont(font)
        self.box_projeto.setStyleSheet(css_inpt_objects)
        self.box_projeto.setObjectName("box_projeto")
        self.lbl_projeto = QtWidgets.QLabel(self.centralwidget)
        self.lbl_projeto.setGeometry(QtCore.QRect(70, 290, 81, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_projeto.setFont(font)
        self.lbl_projeto.setObjectName("lbl_projeto")
        self.lbl_equipe = QtWidgets.QLabel(self.centralwidget)
        self.lbl_equipe.setGeometry(QtCore.QRect(70, 350, 131, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_equipe.setFont(font)
        self.lbl_equipe.setObjectName("lbl_equipe")
        self.box_equipe = QtWidgets.QComboBox(self.centralwidget)
        self.box_equipe.setGeometry(QtCore.QRect(160, 350, 221, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        self.box_equipe.setFont(font)
        self.box_equipe.setStyleSheet(css_inpt_objects)
        self.box_equipe.setObjectName("box_equipe")
        
        self.btn_salvar_agenda = QtWidgets.QPushButton(self.centralwidget)
        self.btn_salvar_agenda.setGeometry(QtCore.QRect(160, 400, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.btn_salvar_agenda.setFont(font)
        self.btn_salvar_agenda.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_salvar_agenda.setStyleSheet("background-color: rgb(47, 79, 79);\n"
"background-color: rgb(0, 62, 91);\n"
"color: rgb(255, 255, 255);")
        self.btn_salvar_agenda.setObjectName("btn_salvar_agenda")
        
        self.lbl_falha = QtWidgets.QLabel(self.centralwidget)
        self.lbl_falha.setGeometry(QtCore.QRect(120, 440, 150, 51))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_falha.setStyleSheet("color: rgb(255, 0, 0);")
        self.lbl_falha.setFont(font)
        self.lbl_falha.setObjectName("lbl_falha")
        self.lbl_falha.setHidden(True)
        
        self.btn_cancelar_agenda = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cancelar_agenda.setGeometry(QtCore.QRect(280, 400, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.btn_cancelar_agenda.setFont(font)
        self.btn_cancelar_agenda.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_cancelar_agenda.setStyleSheet("background-color: rgb(47, 79, 79);\n"
"color: rgb(255, 255, 255);")
        self.btn_cancelar_agenda.setObjectName("btn_cancelar_agenda")
        
        self.titulo_cadastro = QtWidgets.QLabel(self.centralwidget)
        self.titulo_cadastro.setGeometry(QtCore.QRect(180, 30, 321, 41))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(20)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.titulo_cadastro.setFont(font)
        self.titulo_cadastro.setStyleSheet("color: rgb(0, 24, 72);\n")
        self.titulo_cadastro.setAlignment(QtCore.Qt.AlignCenter)
        self.titulo_cadastro.setObjectName("titulo_cadastro")
        
        self.btn_consultar_viagem = QtWidgets.QPushButton(self.centralwidget)
        self.btn_consultar_viagem.setGeometry(QtCore.QRect(300, 450, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.btn_consultar_viagem.setFont(font)
        self.btn_consultar_viagem.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_consultar_viagem.setStyleSheet("background-color: rgb(66, 66, 66);\n"
"color: rgb(255, 255, 255);")
        self.btn_consultar_viagem.setObjectName("btn_consultar_viagem")
        
        self.lbl_categoria = QtWidgets.QLabel(self.centralwidget)
        self.lbl_categoria.setGeometry(QtCore.QRect(50, 180, 131, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_categoria.setFont(font)
        self.lbl_categoria.setObjectName("lbl_categoria")
        
        self.box_categoria = QtWidgets.QComboBox(self.centralwidget)
        self.box_categoria.setGeometry(QtCore.QRect(160, 180, 221, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        self.box_categoria.setFont(font)
        self.box_categoria.setStyleSheet(css_inpt_objects)
        self.box_categoria.setObjectName("box_categoria")
        
        self.lbl_imagem = QtWidgets.QLabel(self.centralwidget)
        self.lbl_imagem.setGeometry(QtCore.QRect(60, 0, 111, 91))
        font = QtGui.QFont()
        font.setFamily("MS UI Gothic")
        self.lbl_imagem.setFont(font)
        self.lbl_imagem.setText("")
        self.lbl_imagem.setPixmap(QtGui.QPixmap("Img\logo quadrada_.png"))
        self.lbl_imagem.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_imagem.setWordWrap(False)
        self.lbl_imagem.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.lbl_imagem.setObjectName("lbl_imagem")
        
        self.btn_consultar_plantao = QtWidgets.QPushButton(self.centralwidget)
        self.btn_consultar_plantao.setGeometry(QtCore.QRect(450, 450, 141, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.btn_consultar_plantao.setFont(font)
        self.btn_consultar_plantao.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_consultar_plantao.setStyleSheet("background-color: rgb(66, 66, 66);\n"\
                          "color: rgb(255, 255, 255)")
        self.btn_consultar_plantao.setObjectName("btn_consultar_plantao")
        self.btn_cadastrar_analista = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cadastrar_analista.setGeometry(QtCore.QRect(460, 120, 31, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        
        self.btn_cadastrar_analista.setFont(font)
        self.btn_cadastrar_analista.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_cadastrar_analista.setStyleSheet(css_btn_objects)
        self.btn_cadastrar_analista.setObjectName("btn_cadastrar_analista")
        
        self.btn_cadastrar_projeto = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cadastrar_projeto.setGeometry(QtCore.QRect(390, 350, 31, 31))
        self.btn_cadastrar_projeto.setFont(font)
        self.btn_cadastrar_projeto.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_cadastrar_projeto.setStyleSheet(css_btn_objects)
        self.btn_cadastrar_projeto.setObjectName("btn_cadastrar_projeto")
        
        self.btn_cadastrar_equipe = QtWidgets.QPushButton(self.centralwidget)
        self.btn_cadastrar_equipe.setGeometry(QtCore.QRect(390, 290, 31, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.btn_cadastrar_equipe.setFont(font)
        self.btn_cadastrar_equipe.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_cadastrar_equipe.setStyleSheet(css_btn_objects)
        self.btn_cadastrar_equipe.setObjectName("btn_cadastrar_equipe")        
        
        self.box_analist = QtWidgets.QComboBox(self.centralwidget)
        self.box_analist.setGeometry(QtCore.QRect(160, 120, 291, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(13)
        self.box_analist.setFont(font)
        self.box_analist.setStyleSheet(css_inpt_objects)
        self.box_analist.setObjectName("box_analist")
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)
        
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self: object) -> None:
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("self", "Cronograma FadamiPay"))
        self.titulo_cadastro.setText(_translate("self", "Cronograma FadamiPay"))
        self.lbl_analista.setText(_translate("self", "Analista:"))
        self.lbl_data_inicio.setText(_translate("self", "Data Inicial:"))
        self.lbl_data_fim.setText(_translate("self", "Até:"))
        self.lbl_projeto.setText(_translate("self", "Projeto:"))
        self.lbl_equipe.setText(_translate("self", "Equipe:"))
        self.lbl_categoria.setText(_translate("self", "Categoria:"))
        self.lbl_falha.setText(_translate("self", "Falha ao cadastrar\nInsira os dados\ncorretamente"))
        self.btn_salvar_agenda.setText(_translate("self", "Salvar"))
        self.btn_cancelar_agenda.setText(_translate("self", "Cancelar"))
        self.btn_consultar_viagem.setText(_translate("self", "Consultar Viagem"))
        self.btn_consultar_plantao.setText(_translate("self", "Consultar Plantão"))
        self.btn_cadastrar_analista.setText(_translate("self", "+"))
        self.btn_cadastrar_equipe.setText(_translate("self", "+"))
        self.btn_cadastrar_projeto.setText(_translate("self", "+"))
        self.lbl_autores.setText(_translate("self", "Desenvolvido por: Débora Melo\nParticipação de: Iago Barbosa"))