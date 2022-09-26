from View.EditarProgramacao import EditarProgramacao
from Model.Enum.TipoProgramacaoEnum import TipoProgramacaoEnum as Tipo
from Model.Enum.TipoTelaEnum import TipoTelaEnum
from View.PainelOpcao import PainelOpcao
from Model import (
                   Excel,
                   Pdf,
                   Analista,
                   Equipe,
                   Projeto
                   )
from Controller import ConnectionDB as DbUtil
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from PyQt5.QtGui import QIcon
import datetime, calendar


class ListagemViagem(QMainWindow):
    
    def __init__(self:object, db:DbUtil, agenda_tipo: Tipo, parent=None) -> None:
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.db: DbUtil = db
        self.setup_ui()
        self.box_dados = (self.box_analista, self.box_equipe, self.box_projeto)
        self.agenda_tipo = agenda_tipo
        self.iniciar_tabela()
        self.popular_boxes()
        self.btn_events()
    
    def btn_events(self: object) -> None:
        self.inpt_data_inicio.dateTimeChanged.connect(self.alterar_data_fim)
        self.btn_pdf.clicked.connect(lambda: Pdf(self.db,
                                                self.agenda_tipo, 
                                                self.adquirir_dados_tabela()))
        self.btn_excel.clicked.connect(lambda: Excel(self.db, 
                                                    self.agenda_tipo, 
                                                    self.adquirir_dados_tabela()))
        
        self.btn_editar.clicked.connect(lambda: self.open_window(EditarProgramacao(self.db,
                                                                            self.preparar_dados(),
                                                                            self.agenda_tipo,
                                                                            self)))
            
        self.btn_filtrar.clicked.connect(lambda: self.popular_tabela(self.filtrar_dados()))
        self.btn_limpar.clicked.connect(self.limpar_tela)
    
    def limpar_tela(self: object) -> None:
        self.popular_boxes()
        self.iniciar_tabela()

    def adquirir_dados_tabela(self):
        dados_retorno = []
        for x in range(self.listagem.rowCount()):
            dados_ler = []
            for y in range(1, 7):
                dados_ler.append(self.listagem.item(x, y).text())
            dados_retorno.append(dados_ler)
        return dados_retorno
        
    def open_window(self: object, tela:QMainWindow) -> None:
        tela_atual:QMainWindow = tela
        tela_atual.show()

    def transformar_datetime(self: object, data) -> str:
        data = datetime.datetime(int(data.split('/')[2]), int(data.split('/')[1]),
        int(data.split('/')[0])).strftime('%Y-%m-%d')
        return data

    def iniciar_tabela(self: object) -> None:
        if self.agenda_tipo == Tipo.Viagem:
            dados = self.db.execute_query("SELECT * FROM VW_LISTA_VIAGEM;")
        else:
            dados = self.db.execute_query("SELECT * FROM VW_LISTA_PLANTAO;")
        if dados != None:
                dados.sort(key=lambda x: x[0])
        self.popular_tabela(dados)

    def alterar_data_fim(self: object) -> None:
        data_inicio = datetime.datetime.strptime(self.inpt_data_inicio.text(), '%d/%m/%Y')
        data_fim = datetime.datetime.strptime(self.inpt_data_fim.text(), '%d/%m/%Y')
        if data_inicio.month != data_fim.month or data_inicio.year != data_fim.year:
            self.inpt_data_fim.setDateTime(QtCore.QDateTime(datetime.datetime(
                day=calendar.monthrange(data_inicio.year,
                                        data_inicio.month)[1], 
                month=data_inicio.month,
                year=data_inicio.year), QtCore.QTime(0, 0, 0)))
    
    def filtrar_dados(self: object) -> tuple:        
        analistas = tuple(map(lambda analista: Analista(codigo=analista[0], 
                                                        nome=analista[1],
                                                        cd_status=analista[2]),
                            self.db.execute_procedure("SPC_ANALISTAS", (None, 1))))
        equipes = tuple(map(lambda equipe: Equipe(codigo=equipe[0], nome=equipe[1]),
                            self.db.execute_procedure('SPC_EQUIPE', (None, 1))))
        projetos = tuple(map(lambda projeto: Projeto(codigo=projeto[0], nome=projeto[1]),
                            self.db.execute_procedure('SPC_PROJETO', (None, 1))))
        dados = (analistas, equipes, projetos)
        dados_utilizados = []
        if self.box_status.currentText() ==  "Ativo":
            status = 1
        elif self.box_status.currentText() ==  "Inativo":
            status = 0
        else:
            status = None
        if self.agenda_tipo == Tipo.Viagem:
            dados_utilizados.extend([0, 
                                    f'{self.transformar_datetime(self.inpt_data_inicio.text())}', 
                                    f'{self.transformar_datetime(self.inpt_data_fim.text())}'])
        else:
            dados_utilizados.extend([1,
                                    f'{self.transformar_datetime(self.inpt_data_inicio.text())}',
                                    f'{self.transformar_datetime(self.inpt_data_fim.text())}'])
        for indice in range(len(dados)):
            for indice2 in range(len(dados[indice])):
                if type(dados[indice][indice2]) is Analista:
                    if len(dados[indice][indice2].nome.split()) > 1:
                        nome = f"{dados[indice][indice2].nome.split()[0]} {dados[indice][indice2].nome.split()[1][0]}"
                    else:
                        nome = f"{dados[indice][indice2].nome}"
                else:
                    nome = dados[indice][indice2].nome
                if nome == self.box_dados[indice].currentText():
                    dados_utilizados.append(dados[indice][indice2].codigo)  
                    break  
                if indice2 == (len(dados[indice]) - 1):
                    dados_utilizados.append(None)
        dados_utilizados.append(status)
        resultado = self.db.execute_procedure("SPC_FILTRO_TABELAS", dados_utilizados)
        if resultado == None:
            return self.limpar_tabela()
        if len(resultado) > 0:
            resultado.sort(key=lambda x: x[0])
        return resultado
    
    def preparar_dados(self: object) -> None:
        try:
            linhaexata = self.listagem.currentRow()
            lista_dados = (
                        self.listagem.item(linhaexata, 0).text(),
                        self.listagem.item(linhaexata,1).text(),
                        self.listagem.item(linhaexata, 2).text(), 
                        self.listagem.item(linhaexata, 3).text(),
                        datetime.datetime(
                                        day=int(self.listagem.item(linhaexata,4).text().split('/')[0]),
                                        month=int(self.listagem.item(linhaexata,4).text().split('/')[1]),
                                        year=int(self.listagem.item(linhaexata,4).text().split('/')[2])).date(),
                        datetime.datetime(
                                        day=int(self.listagem.item(linhaexata,5).text().split('/')[0]),
                                        month=int(self.listagem.item(linhaexata,5).text().split('/')[1]),
                                        year=int(self.listagem.item(linhaexata,5).text().split('/')[2])).date(),
                        self.listagem.item(linhaexata, 6).text()
                        )
            return lista_dados    
        except Exception as e:
            self.open_window(PainelOpcao(TipoTelaEnum.DialogError,
                                         "Não existem dados à serem editados.",
                                         self))

    def popular_boxes(self: object) -> None:
        analistas = tuple(map(lambda analista: Analista(codigo=analista[0], id_equipe=analista[3],
                                                        nome=analista[1]),
                              self.db.execute_procedure("SPC_ANALISTAS", (1, 0))))
        equipes = tuple(map(lambda equipe: Equipe(codigo=equipe[0], nome=equipe[1]),
                            self.db.execute_procedure('SPC_EQUIPE', (1, 0))))
        projetos = tuple(map(lambda projeto: Projeto(codigo=projeto[0], nome=projeto[1]),
                             self.db.execute_procedure('SPC_PROJETO', (1, 0))))
        dados = (analistas, equipes, projetos)
        for x in self.box_dados:
            x.clear()    
            x.addItem('Selecione')
        for indice in range(len(dados)):
            for indice2 in range(len(dados[indice])):
                if type(dados[indice][indice2]) is Analista:
                    sobrenome = dados[indice][indice2].nome.split()[1][0] if len(dados[indice][indice2].nome.split()) > 1 else ''
                    nome = f"{dados[indice][indice2].nome.split()[0]} {sobrenome}"
                    self.box_dados[indice].addItem(nome)
                else:
                    self.box_dados[indice].addItem(dados[indice][indice2].nome)
        self.box_status.clear()
        self.box_status.addItem('Todos')
        self.box_status.addItem('Ativo')
        self.box_status.addItem('Inativo')
    
    def popular_tabela(self: object, dados: tuple) -> None:
        if dados is None:
            return
        self.listagem.setColumnCount(7)
        tipo = "Plantão" if self.agenda_tipo == Tipo.Plantao else "Viagem"
        if len(dados) > 0:
            self.listagem.setRowCount(len(dados))
            for indice in range(len(dados)):
                for valor in range(7):
                    if type(dados[indice][valor]) is datetime.date:
                        self.listagem.setItem(indice,valor,QTableWidgetItem(dados[indice][valor].strftime('%d/%m/%Y')))
                    else:
                        self.listagem.setItem(indice,valor,QTableWidgetItem(str(dados[indice][valor])))                    
            self.listagem.verticalHeader().setVisible(False)
        self.listagem.setHorizontalHeaderLabels([tipo, 
                                                 'Analista', 
                                                 'Equipe',
                                                 'Projeto',
                                                 'Data Inicio',
                                                 'Data Fim',
                                                 'Horas Adc.'])
        self.listagem.resizeColumnsToContents()
        self.listagem.resizeRowsToContents()

    def limpar_tabela(self:object) -> None:
        self.listagem.clear()
        self.listagem.setColumnCount(7)
        tipo = "Plantão" if self.agenda_tipo == Tipo.Plantao else "Viagem"
        self.listagem.verticalHeader().setVisible(False)
        self.listagem.setHorizontalHeaderLabels([tipo 
                                                 ,'Analista'
                                                 ,'Equipe'
                                                 ,'Projeto'
                                                 ,'Data Inicio'
                                                 ,'Data Fim'
                                                 ,'Horas Adc.'])

    def setup_ui(self: object) -> None:
        css_inpt_objects = "background-color: rgb(255, 255, 255);\n"\
                           "color: #333333;"
        self.setObjectName("listagem_viagem")
        self.resize(728, 520)
        self.setWindowIcon(QtGui.QIcon('Img/app_logo.png'))
        self.setMinimumSize(QtCore.QSize(728, 520))
        self.setMaximumSize(QtCore.QSize(728, 520))
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.titulo_pagina = QtWidgets.QLabel(self.centralwidget)
        self.titulo_pagina.setGeometry(QtCore.QRect(205, 0, 351, 51))
        font = QtGui.QFont()
        font.setFamily("Yu Gothic Light")
        font.setPointSize(18)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.titulo_pagina.setFont(font)
        self.titulo_pagina.setStyleSheet("color: rgb(47, 79, 79);")
        self.titulo_pagina.setObjectName("titulo_pagina")
        self.listagem = QtWidgets.QTableWidget(self.centralwidget)
        self.listagem.setGeometry(QtCore.QRect(40, 50, 571, 401))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semibold")
        font.setPointSize(11)
        font.setBold(True)
        font.setWeight(75)
        self.listagem.setFont(font)
        self.listagem.setToolTipDuration(-4)
        self.listagem.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.listagem.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.listagem.setColumnCount(0)
        self.listagem.setObjectName("listagem")
        self.listagem.setRowCount(0)
        self.btn_editar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_editar.setGeometry(QtCore.QRect(390, 460, 81, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_editar.setFont(font)
        self.btn_editar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_editar.setStyleSheet("background-color: rgb(170, 170, 127);")
        self.btn_editar.setObjectName("btn_editar")
        self.lbl_imagem = QtWidgets.QLabel(self.centralwidget)
        self.lbl_imagem.setGeometry(QtCore.QRect(165, 0, 41, 41))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.lbl_imagem.setFont(font)
        self.lbl_imagem.setText("")
        self.lbl_imagem.setPixmap(QtGui.QPixmap("Img\logo.png"))
        self.lbl_imagem.setObjectName("lbl_imagem")
        self.btn_pdf = QtWidgets.QPushButton(self.centralwidget)
        self.btn_pdf.setGeometry(QtCore.QRect(550, 460, 61, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_pdf.setFont(font)
        self.btn_pdf.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_pdf.setStyleSheet("color: rgb(255, 255, 255);\n"
"background-color: rgb(106, 0, 0);\n"
"")
        self.btn_pdf.setObjectName("btn_pdf")
        self.btn_excel = QtWidgets.QPushButton(self.centralwidget)
        self.btn_excel.setGeometry(QtCore.QRect(480, 460, 61, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.btn_excel.setFont(font)
        self.btn_excel.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_excel.setStyleSheet("background-color: rgb(170, 170, 127);\n"
"color: rgb(255, 255, 255);\n"
"background-color: rgb(38, 76, 0);")
        self.btn_excel.setObjectName("btn_excel")
        self.setCentralWidget(self.centralwidget)
        
        self.lbl_data_inicio = QtWidgets.QLabel(self.centralwidget)
        self.lbl_data_inicio.setGeometry(QtCore.QRect(620, 45, 71, 20))
        self.lbl_data_inicio.setObjectName("lbl_data_inicio")
        self.inpt_data_inicio = QtWidgets.QDateEdit(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(9)
        self.inpt_data_inicio.setFont(font)
        self.inpt_data_inicio.setGeometry(QtCore.QRect(620, 65, 101, 21))
        ano = datetime.datetime.now().year
        mes = datetime.datetime.now().month
        self.inpt_data_inicio.setDateTime(QtCore.QDateTime(datetime.datetime(day=1,
                                                                             month=mes,
                                                                             year=ano),
                                                           QtCore.QTime(0, 0, 0)))
        self.inpt_data_inicio.setStyleSheet(css_inpt_objects)
        self.inpt_data_inicio.setObjectName("inpt_data_inicio")
        
        self.lbl_data_fim = QtWidgets.QLabel(self.centralwidget)
        self.lbl_data_fim.setGeometry(QtCore.QRect(620, 105, 61, 20))
        self.lbl_data_fim.setObjectName("lbl_data_fim")
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(9)
        self.inpt_data_fim = QtWidgets.QDateEdit(self.centralwidget)
        self.inpt_data_fim.setFont(font)
        self.inpt_data_fim.setGeometry(QtCore.QRect(620, 125, 101, 21))
        self.inpt_data_fim.setObjectName("inpt_data_fim")
        self.inpt_data_fim.setDateTime(QtCore.QDateTime(datetime.datetime(
            day=calendar.monthrange(ano, mes)[1],
            month=mes,
            year=ano),
                                                        QtCore.QTime(0, 0, 0)))
        self.inpt_data_fim.setStyleSheet(css_inpt_objects)

        self.lbl_analista = QtWidgets.QLabel(self.centralwidget)
        self.lbl_analista.setGeometry(QtCore.QRect(620, 165, 51, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lbl_analista.setFont(font)
        self.lbl_analista.setObjectName("lbl_analista")
        self.box_analista = QtWidgets.QComboBox(self.centralwidget)
        self.box_analista.setStyleSheet(css_inpt_objects)
        font = QtGui.QFont()
        font.setBold(True)
        self.box_analista.setFont(font)
        self.box_analista.setGeometry(QtCore.QRect(620, 185, 101, 22))
        self.box_analista.setObjectName("box_analista")
        
        self.lbl_equipe = QtWidgets.QLabel(self.centralwidget)
        self.lbl_equipe.setGeometry(QtCore.QRect(620, 225, 51, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lbl_equipe.setFont(font)
        self.lbl_equipe.setObjectName("lbl_equipe")
        self.box_equipe = QtWidgets.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        self.box_equipe.setFont(font)
        self.box_equipe.setGeometry(QtCore.QRect(620, 245, 101, 22))
        self.box_equipe.setStyleSheet(css_inpt_objects)
        self.box_equipe.setObjectName("box_equipe")
        
        self.lbl_projeto = QtWidgets.QLabel(self.centralwidget)
        self.lbl_projeto.setGeometry(QtCore.QRect(620, 285, 51, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lbl_projeto.setFont(font)
        self.lbl_projeto.setObjectName("lbl_projeto")
        self.box_projeto = QtWidgets.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        self.box_projeto.setFont(font)
        self.box_projeto.setGeometry(QtCore.QRect(620, 305, 101, 22))
        self.box_projeto.setStyleSheet(css_inpt_objects)
        self.box_projeto.setObjectName("box_projeto")

        self.lbl_status = QtWidgets.QLabel(self.centralwidget)
        self.lbl_status.setGeometry(QtCore.QRect(620, 345, 51, 20))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.lbl_status.setFont(font)
        self.lbl_status.setObjectName("lbl_status")
        self.box_status = QtWidgets.QComboBox(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        self.box_status.setFont(font)
        self.box_status.setGeometry(QtCore.QRect(620, 365, 101, 22))
        self.box_status.setStyleSheet(css_inpt_objects)
        self.box_status.setObjectName("box_status")

        self.btn_filtrar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_filtrar.setGeometry(QtCore.QRect(630, 405, 81, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)
        font.setWeight(75)
        self.btn_filtrar.setFont(font)
        self.btn_filtrar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_filtrar.setStyleSheet("background-color: rgb(51, 102, 153);\n color: rgb(255, 255, 255);")
        self.btn_filtrar.setObjectName("btn_filtrar")
        self.btn_filtrar.setIcon(QIcon('Img/filtro_1_branco.png'))
    

        self.btn_limpar = QtWidgets.QPushButton(self.centralwidget)
        self.btn_limpar.setGeometry(QtCore.QRect(630, 445, 81, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(10)
        font.setWeight(75)
        self.btn_limpar.setFont(font)
        self.btn_limpar.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_limpar.setObjectName("btn_limpar")
        self.btn_limpar.setIcon(QIcon('Img/filtro.png'))

        # A linha de cada elemento, entonra-se abaixo dos itens
        # Ex: O line_data_inicio fica abaixo do inpt_data_inicio
        self.line_data_inicio = QtWidgets.QFrame(self.centralwidget)
        self.line_data_inicio.setGeometry(QtCore.QRect(610, 90, 121, 16))
        self.line_data_inicio.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_data_inicio.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_data_inicio.setObjectName("line_data_inicio")
        self.line_data_fim = QtWidgets.QFrame(self.centralwidget)
        self.line_data_fim.setGeometry(QtCore.QRect(610, 150, 121, 16))
        self.line_data_fim.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_data_fim.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_data_fim.setObjectName("line_data_fim")
        self.line_analista = QtWidgets.QFrame(self.centralwidget)
        self.line_analista.setGeometry(QtCore.QRect(610, 210, 121, 16))
        self.line_analista.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_analista.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_analista.setObjectName("line_analista")
        self.line_equipe = QtWidgets.QFrame(self.centralwidget)
        self.line_equipe.setGeometry(QtCore.QRect(610, 270, 121, 16))
        self.line_equipe.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_equipe.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_equipe.setObjectName("line_equipe")
        self.line_projeto = QtWidgets.QFrame(self.centralwidget)
        self.line_projeto.setGeometry(QtCore.QRect(610, 332, 121, 16))
        self.line_projeto.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_projeto.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_projeto.setObjectName("line_projeto")
        self.line_status = QtWidgets.QFrame(self.centralwidget)
        self.line_status.setGeometry(QtCore.QRect(610, 390, 121, 16))
        self.line_status.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_status.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_status.setObjectName("line_status")
        
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self: object) -> None:
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("listagem_viagem", " "))
        self.titulo_pagina.setText(_translate("listagem_viagem", "Programações Agendadas"))
        self.btn_editar.setText(_translate("listagem_viagem", "Editar"))
        self.btn_pdf.setText(_translate("listagem_viagem", "PDF"))
        self.btn_excel.setText(_translate("listagem_viagem", "Excel"))
        self.lbl_data_inicio.setText(_translate("listagem_viagem", "Data Início:"))
        self.lbl_data_fim.setText(_translate("listagem_viagem", "Data Fim:"))
        self.lbl_equipe.setText(_translate("listagem_viagem", "Equipe:"))
        self.lbl_projeto.setText(_translate("listagem_viagem", "Projeto:"))
        self.lbl_status.setText(_translate("listagem_viagem", "Status:"))
        self.lbl_analista.setText(_translate("listagem_viagem", "Analista:"))
        self.btn_filtrar.setText(_translate("listagem_viagem", "Filtrar"))
        self.btn_limpar.setText(_translate("listagem_viagem", "Limpar"))
        