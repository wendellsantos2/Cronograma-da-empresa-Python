from Model.Enum.TipoProgramacaoEnum import TipoProgramacaoEnum as Tipo
from reportlab.pdfgen import canvas as pdf_gen
from Controller import ConnectionDB
import os, datetime

class Pdf:
    
    def __init__(self:object, db: ConnectionDB, tipo: Tipo, dadosLidos: tuple) -> None:
        self.db = db
        self.caminho_pdf:str = f"C:\\Users\\{os.getlogin()}\\Downloads"
        if tipo == Tipo.Plantao:
            # dadosLidos = self.db.execute_query("SELECT A.NOME_ANALISTA,E.NOME_EQUIPE,P.NOME_PROJETO, VA.DATA_PLANTAO_INICIO, VA.DATA_PLANTAO_FIM,VA.HORA_ADICIONAL FROM ANALISTAS AS A INNER JOIN PLANTAO_ANALISTAS AS VA ON VA.ID_ANALISTA=A.ID_ANALISTA INNER JOIN CATEGORIA AS C ON C.ID_CATEGORIA=VA.ID_CATEGORIA INNER JOIN EQUIPE AS E ON E.ID_EQUIPE=VA.ID_EQUIPE INNER JOIN PROJETOS AS P ON P.ID_PROJETO = VA.ID_PROJETO WHERE A.CD_STATUS = 1")
            self.categoria = 'Plantões'
            self.data_inicio = 'Data Inicio'
            self.data_fim = 'Data Fim'
            self.nome_arquivo = f"CronogramaViagemFadamiPay-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')}.pdf"    
        else:
            # dadosLidos = self.db.execute_query("SELECT A.NOME_ANALISTA,E.NOME_EQUIPE,P.NOME_PROJETO, VA.DATA_VIAGEM_INICIO, VA.DATA_VIAGEM_FIM,VA.HORA_ADICIONAL FROM ANALISTAS AS A INNER JOIN VIAGENS_ANALISTAS AS VA ON VA.ID_ANALISTA=A.ID_ANALISTA INNER JOIN CATEGORIA AS C ON C.ID_CATEGORIA=VA.ID_CATEGORIA INNER JOIN EQUIPE AS E ON E.ID_EQUIPE=VA.ID_EQUIPE INNER JOIN PROJETOS AS P ON P.ID_PROJETO = VA.ID_PROJETO WHERE A.CD_STATUS = 1;")
            self.categoria = 'Viagens'
            self.data_inicio = 'Data Ida'
            self.data_fim = 'Data Volta'
            self.nome_arquivo = f"CronogramaPlantãoFadamiPay-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')}"
        arquivos_iguais = len(tuple(filter(lambda arquivo: self.nome_arquivo in arquivo, os.listdir(self.caminho_pdf))))
        if arquivos_iguais > 0:
            self.nome_arquivo = f"{self.nome_arquivo}({arquivos_iguais+1})"
        self.nome_arquivo = f"{self.nome_arquivo}.pdf"
        self.montar_pdf(dadosLidos)
            
    def montar_pdf(self: object, dadosLidos:list) -> None:
        linha = 0
        pdf = pdf_gen.Canvas(f"{self.caminho_pdf}\\{self.nome_arquivo}") # Nome do arquivo dentro da pasta do projeto
        pdf.setFont("Times-Bold", 20) #Fonte do título
        pdf.drawString(200,800,f"Programação {self.categoria}") # 200[x] e 800[y]: Posição
        pdf.setFont("Times-Bold", 14)
        header = ("Analistas", "Equipe", "Projeto", self.data_inicio, self.data_fim, "Hrs Adc")
        coordenadas = (20, 145, 245, 355, 445, 535)
        for indice_header in range(len(coordenadas)):
            pdf.drawString(coordenadas[indice_header], 750 + 20, "---------------------------")
            pdf.drawString(coordenadas[indice_header], 750, header[indice_header])
        dados_inseridos = 0
        for indice_linha in range(len(dadosLidos)):
            linha += 50
            if dados_inseridos == 12:
                pdf.showPage()
                dados_inseridos = 0
                linha = 50
                pdf.setFont("Times-Bold", 20) #Fonte do título
                pdf.drawString(200, 
                               800,
                               f"Programação {self.categoria}")
                pdf.setFont("Times-Bold", 14)
                for indice_header in range(len(coordenadas)):
                    pdf.drawString(coordenadas[indice_header], 750 + 20,
                                   "---------------------------")
                    pdf.drawString(coordenadas[indice_header], 750, header[indice_header])
            for indice_coluna in range(len(dadosLidos[indice_linha])):
                pdf.setFont("Times-Bold", 12)
                pdf.drawString(coordenadas[indice_coluna], 750  - linha,
                               str(dadosLidos[indice_linha][indice_coluna]))
            dados_inseridos += 1
            
        pdf.save()
        os.system(f'start {self.caminho_pdf}\\{self.nome_arquivo}')

if __name__ == '__main__':
    Pdf(Tipo().Plantao)