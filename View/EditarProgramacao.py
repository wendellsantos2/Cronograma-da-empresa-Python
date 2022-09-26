from Controller import ConnectionDB
from Model.Enum.TipoProgramacaoEnum import TipoProgramacaoEnum as Tipo
from Model import ( Analista,
                    Equipe,
                    Categoria,
                    Projeto)
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
import datetime, calendar


class EditarProgramacao(QDialog):
    
    def __init__(self: object, db: ConnectionDB, box_dados_usados: tuple, tipo_programacao: Tipo, parent=None) -> None:
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.db: ConnectionDB = db
        self.parent = parent
        self.tipo_programacao = tipo_programacao
        self.box_dados_usados= box_dados_usados
        self.setup_ui()
        boxDados: tuple = (self.box_analista,
                           self.box_equipe,
                           self.box_projeto)
        self.popular_boxes(self.box_dados_usados,
                           boxDados)
        self.btn_events()
        
    def popular_boxes(self: object, box_dados_usados:tuple, boxDados: tuple) -> None:
        for x in boxDados:
            x.clear()
        try:
            self.inpt_data_inicio.setDate(box_dados_usados[4])
            self.inpt_data_fim.setDate(box_dados_usados[5])

            tuple(boxDados[(x - 1)].addItem(box_dados_usados[x].strip()) for x in range(1, (len(box_dados_usados) - 3)))

            analistas = tuple(map(lambda analista: Analista(codigo=analista[0],
                                                            id_equipe=analista[4],
                                                            nome=analista[1]),
                                self.db.execute_procedure('SPC_ANALISTAS', (1, 0))))
            equipes = tuple(map(lambda equipe: Equipe(codigo=equipe[0],
                                                    nome=equipe[1]),
                                self.db.execute_procedure('SPC_EQUIPE', (1, 0))))
            
            projetos = tuple(map(lambda projeto: Projeto(codigo=projeto[0], 
                                                        nome=projeto[1]),
                                self.db.execute_procedure('SPC_PROJETO', (1, 0))))
            dados_query = []
            dados = (analistas, equipes, projetos)
            
            for dado in dados:
                for tipo in dado:
                    if tipo.nome in box_dados_usados:
                        dados_query.append(tipo.codigo)
                        
            if self.tipo_programacao == Tipo.Viagem:
                query = "SELECT OBSERVACAO, CD_STATUS FROM VIAGENS_ANALISTAS "\
                        f"WHERE ID_VIAGEM_ANALISTAS = {self.box_dados_usados[0]}"                   
            else:
                query = "SELECT OBSERVACAO, CD_STATUS FROM PLANTAO_ANALISTAS "\
                        f"WHERE ID_PLANTAO_ANALISTAS = {self.box_dados_usados[0]}"
                        
            dados_obs_e_status = self.db.execute_query(query)[0]
            if dados_obs_e_status[0] != None:
                self.inpt_text.setText(dados_obs_e_status[0].strip()) 
            
            if dados_obs_e_status[1] == 1:
                if self.tipo_programacao == Tipo.Viagem:
                    self.lbl_status_viagem.setText("Ativa")    
                else:
                    self.lbl_status_viagem.setText("Ativo")
            else:
                if self.tipo_programacao == Tipo.Viagem:
                    self.lbl_status_viagem.setText("Inativa")    
                else:
                    self.lbl_status_viagem.setText("Inativo")
            
            for indice in range(len(dados)):
                for indice2 in range(len(dados[indice])):
                    if boxDados[indice].findText(dados[indice][indice2].nome) == -1:
                        boxDados[indice].addItem(dados[indice][indice2].nome)
            
            if box_dados_usados[5] >= datetime.date.today() and dados_obs_e_status[1] == 1:
                self.btn_excluir_programacao.setEnabled(True)
            else:
                self.btn_excluir_programacao.setEnabled(False)
                self.btn_excluir_programacao.setStyleSheet("background-color: #8c8c8c;")
        
        except Exception as e:
            self.close()
            pass
            

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
        self.btn_salvar_alteracao.clicked.connect(lambda: self.alterar_dados())
        self.btn_excluir_programacao.clicked.connect(self.excluir_dados)
        self.inpt_data_inicio.dateTimeChanged.connect(self.alterar_data_fim)
    
    def excluir_dados(self: object) -> None:
        tipo_categoria = 0 if self.tipo_programacao == Tipo.Viagem else 1
        id_programacao = self.box_dados_usados[0]
        self.db.execute_procedure('SPD_VIAGEM_PLANTAO', (tipo_categoria, 
                                                  id_programacao))
        self.close()
        self.parent.filtrar_dados()
        
    # Receber o id da Viagem da página de listagem de Viagens
    def alterar_dados(self: object) -> None:
        dados_id = []
        dados_box = (self.box_analista.currentText(), 
                    self.box_equipe.currentText(), 
                    self.box_projeto.currentText())
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
        
        
        dados = (analistas, equipes, projetos)
        for indice_dados in range(len(dados)):
            for indice_lista in range(len(dados[indice_dados])):
                for conteudo in dados_box:
                    if dados[indice_dados][indice_lista].nome == conteudo:
                        dados_id.append(dados[indice_dados][indice_lista].codigo)
        data_inicio = self.inpt_data_inicio.text()  
        data_inicio = datetime.datetime(
            int(data_inicio.split('/')[2]),
            int(data_inicio.split('/')[1]),
            int(data_inicio.split('/')[0])).strftime('%Y-%m-%d')
        data_fim = self.inpt_data_fim.text()
        data_fim = datetime.datetime(
            int(data_fim.split('/')[2]), 
            int(data_fim.split('/')[1]),
            int(data_fim.split('/')[0])).strftime('%Y-%m-%d')

        tipo_categoria = [0, 1] if self.tipo_programacao == Tipo.Viagem else [1, 2]
        
        hora_adicional =  self.box_horas.currentIndex()
        observacao = self.inpt_text.toPlainText()
        id_programacao = self.box_dados_usados[0]
            
        self.db.execute_procedure("SPA_VIAGEM_PLANTAO", (
                                                         tipo_categoria[0],
                                                         id_programacao,
                                                         dados_id[0],
                                                         tipo_categoria[1],
                                                         dados_id[1],
                                                         dados_id[2],
                                                         data_inicio,
                                                         data_fim,
                                                         hora_adicional,
                                                         observacao))
        self.close()
        self.parent.iniciar_tabela()
    
    def setup_ui(self: object) -> None:
        css_inpt_style = "color: #000; background-color: #fff"
        self.setObjectName("Editar Viagens")
        self.resize(611, 459)
        self.setMinimumSize(QtCore.QSize(611, 459))
        self.setMaximumSize(QtCore.QSize(611, 459))
        self.setWindowIcon(QtGui.QIcon('Img/app_logo.png'))
        self.setStyleSheet("alternate-background-color: rgb(225, 225, 225);")
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        
        self.btn_salvar_alteracao = QtWidgets.QPushButton(self.centralwidget)
        self.btn_salvar_alteracao.setGeometry(QtCore.QRect(420, 300, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.btn_salvar_alteracao.setFont(font)
        self.btn_salvar_alteracao.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_salvar_alteracao.setStyleSheet("background-color: rgb(0, 85, 0);\n"
"color: rgb(255, 255, 255);")

        self.btn_excluir_programacao = QtWidgets.QPushButton(self.centralwidget)
        self.btn_excluir_programacao.setGeometry(QtCore.QRect(420, 341, 111, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.btn_excluir_programacao.setFont(font)
        self.btn_excluir_programacao.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_excluir_programacao.setStyleSheet("background-color: #cc0000;\n"
"color: rgb(255, 255, 255);")
        
        
        self.btn_salvar_alteracao.setObjectName("btn_salvar_alteracao")
        self.lbl_analista = QtWidgets.QLabel(self.centralwidget)
        self.lbl_analista.setGeometry(QtCore.QRect(130, 60, 81, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_analista.setFont(font)
        self.lbl_analista.setObjectName("lbl_analista")
        self.lbl_titulo = QtWidgets.QLabel(self.centralwidget)
        self.lbl_titulo.setGeometry(QtCore.QRect(260, 20, 191, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_titulo.setFont(font)
        self.lbl_titulo.setStyleSheet("color: rgb(0, 34, 50);")
        self.lbl_titulo.setObjectName("lbl_titulo")
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(True)
        font.setWeight(75)
        self.box_equipe = QtWidgets.QComboBox(self.centralwidget)
        self.box_equipe.setGeometry(QtCore.QRect(50, 160, 211, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(13)
        self.box_equipe.setFont(font)
        self.box_equipe.setStyleSheet(css_inpt_style)
        self.box_equipe.setObjectName("box_equipe")
        self.box_projeto = QtWidgets.QComboBox(self.centralwidget)
        self.box_projeto.setStyleSheet(css_inpt_style)
        self.box_projeto.setGeometry(QtCore.QRect(320, 90, 221, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(13)
        self.box_projeto.setFont(font)
        self.box_projeto.setObjectName("box_projeto")
        self.lbl_projeto = QtWidgets.QLabel(self.centralwidget)
        self.lbl_projeto.setGeometry(QtCore.QRect(380, 60, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_projeto.setFont(font)
        self.lbl_projeto.setObjectName("lbl_projeto")
        self.lbl_equipe = QtWidgets.QLabel(self.centralwidget)
        self.lbl_equipe.setGeometry(QtCore.QRect(130, 130, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_equipe.setFont(font)
        self.lbl_equipe.setObjectName("lbl_equipe")
        self.inpt_data_inicio = QtWidgets.QDateEdit(self.centralwidget)
        self.inpt_data_inicio.setGeometry(QtCore.QRect(280, 160, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        self.inpt_data_inicio.setFont(font)
        self.inpt_data_inicio.setStyleSheet(css_inpt_style)
        self.inpt_data_inicio.setAlignment(QtCore.Qt.AlignCenter)
        self.inpt_data_inicio.setObjectName("inpt_data_inicio")
        self.inpt_data_fim = QtWidgets.QDateEdit(self.centralwidget)
        self.inpt_data_fim.setGeometry(QtCore.QRect(420, 160, 121, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(13)
        self.inpt_data_fim.setFont(font)
        self.inpt_data_fim.setStyleSheet(css_inpt_style)
        self.inpt_data_fim.setAlignment(QtCore.Qt.AlignCenter)
        self.inpt_data_fim.setObjectName("inpt_data_fim")
        self.lbl_data_inicio = QtWidgets.QLabel(self.centralwidget)
        self.lbl_data_inicio.setGeometry(QtCore.QRect(300, 130, 81, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_data_inicio.setFont(font)
        self.lbl_data_inicio.setObjectName("lbl_data_inicio")
        self.lbl_data_volta = QtWidgets.QLabel(self.centralwidget)
        self.lbl_data_volta.setGeometry(QtCore.QRect(430, 130, 101, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_data_volta.setFont(font)
        self.lbl_data_volta.setObjectName("lbl_data_volta")
        self.lbl_img = QtWidgets.QLabel(self.centralwidget)
        self.lbl_img.setGeometry(QtCore.QRect(220, 10, 41, 41))
        self.lbl_img.setMinimumSize(QtCore.QSize(41, 41))
        self.lbl_img.setMaximumSize(QtCore.QSize(41, 41))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_img.setFont(font)
        self.lbl_img.setText("")
        self.lbl_img.setPixmap(QtGui.QPixmap("Img/logo.png"))
        self.lbl_img.setObjectName("lbl_img")
        self.box_horas = QtWidgets.QComboBox(self.centralwidget)
        self.box_horas.setGeometry(QtCore.QRect(220, 230, 61, 29))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(13)
        self.box_horas.setFont(font)
        self.box_horas.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.box_horas.setAutoFillBackground(True)
        self.box_horas.setStyleSheet("")
        self.box_horas.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContentsOnFirstShow)
        self.box_horas.setObjectName("box_horas")
        self.box_horas.setStyleSheet(css_inpt_style)
        self.lbl_horas_adicionais = QtWidgets.QLabel(self.centralwidget)
        self.lbl_horas_adicionais.setGeometry(QtCore.QRect(50, 230, 161, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_horas_adicionais.setFont(font)
        self.lbl_horas_adicionais.setObjectName("lbl_horas_adicionais")
        self.box_analista = QtWidgets.QComboBox(self.centralwidget)
        self.box_analista.setGeometry(QtCore.QRect(50, 90, 251, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Semilight")
        font.setPointSize(13)
        self.box_analista.setFont(font)
        self.box_analista.setStyleSheet(css_inpt_style)
        self.box_analista.setObjectName("box_analista")
        self.lbl_observacao = QtWidgets.QLabel(self.centralwidget)
        self.lbl_observacao.setGeometry(QtCore.QRect(50, 270, 161, 31))
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_observacao.setFont(font)
        self.lbl_observacao.setObjectName("lbl_observacao")
        self.inpt_text = QtWidgets.QTextEdit(self.centralwidget)
        self.inpt_text.setGeometry(QtCore.QRect(50, 300, 361, 81))
        font = QtGui.QFont()
        font.setFamily("Segoe UI Light")
        font.setPointSize(14)
        self.inpt_text.setFont(font)
        self.inpt_text.setStyleSheet(css_inpt_style)
        self.inpt_text.setObjectName("inpt_text")
        
        self.lbl_status_viagem = QtWidgets.QLabel(self.centralwidget)
        self.lbl_status_viagem.setGeometry(QtCore.QRect(400, 235, 75, 25))
        self.lbl_status_viagem.setStyleSheet("background-color: #e6e6e6; color: #990000;"\
                                             "border: 1px solid #000;")
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_status_viagem.setFont(font)
        self.lbl_status_viagem.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_status_viagem.setObjectName("lbl_status_viagem")
        
        self.lbl_status_viagem_2 = QtWidgets.QLabel(self.centralwidget)
        self.lbl_status_viagem_2.setGeometry(QtCore.QRect(315, 235, 75, 22))
        self.lbl_status_viagem_2.setStyleSheet("color: #000;")
        font = QtGui.QFont()
        font.setFamily("Bahnschrift Light")
        font.setPointSize(14)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.lbl_status_viagem_2.setFont(font)
        self.lbl_status_viagem_2.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_status_viagem_2.setObjectName("lbl_status_viagem_2")
        
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
    
    def retranslateUi(self: object) -> None:
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("self", "Alterar Analista"))
        self.btn_salvar_alteracao.setText(_translate("self", "Salvar"))
        self.btn_excluir_programacao.setText(_translate("self", "Desativar"))
        self.lbl_analista.setText(_translate("self", "Analista"))
        tipo_programacao = "Alterar Viagem" if self.tipo_programacao == Tipo.Viagem else "Alterar Plantão"
        self.lbl_titulo.setText(_translate("self", tipo_programacao)) 

        self.lbl_projeto.setText(_translate("self", "Projeto"))
        self.lbl_equipe.setText(_translate("self", "Equipe"))
        self.lbl_data_inicio.setText(_translate("self", "Data Ida"))
        self.lbl_data_volta.setText(_translate("self", "Data Volta"))
        for horas in range(101):
            self.box_horas.addItem(_translate("self", f"{horas}"))
        self.lbl_horas_adicionais.setText(_translate("self", "Horas Adicionais:"))
        self.lbl_observacao.setText(_translate("self", "Observação:"))
        self.lbl_status_viagem_2.setText(_translate("self", "Status:"))
