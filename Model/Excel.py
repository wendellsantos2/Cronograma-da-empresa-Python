from Model.Enum.TipoProgramacaoEnum import TipoProgramacaoEnum as Tipo
from Controller import ConnectionDB
import os, datetime, xlsxwriter as excel


class Excel:
    
    def __init__(self: object, db: ConnectionDB, tipo: Tipo, dados_lidos: tuple) -> None:
        self.db = db
        self.caminho_excel: str = f"C:\\Users\\{os.getlogin()}\\Downloads"
        coluna = ['Analista', 'Equipe', 'Projeto']
        if tipo == Tipo.Plantao:
            coluna.extend(['Inicio Plantão', 'Fim Plantão','Horas Adicionais'])
            self.categoria = 'Plantões'
            self.data_inicio = 'Data Inicio'
            self.data_fim = 'Data Fim'
            self.nome_arquivo = f"CronogramaViagemFadamiPay-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')}"    
        else:
            coluna.extend(['Inicio Viagem','Fim Viagem','Horas Adicionais'])
            self.categoria = 'Viagens'
            self.data_inicio = 'Data Ida'
            self.data_fim = 'Data Volta'
            self.nome_arquivo = f"CronogramaPlantãoFadamiPay-{datetime.datetime.now().strftime('%d-%m-%Y_%H-%M')}"
        arquivos_iguais = len(tuple(filter(lambda arquivo: self.nome_arquivo in arquivo, os.listdir(self.caminho_excel))))
        if arquivos_iguais > 0:
            self.nome_arquivo = f"{self.nome_arquivo}({arquivos_iguais+1})"
        self.nome_arquivo = f'{self.nome_arquivo}.xlsx'
        self.montar_excel(dados_lidos, coluna)

    def formatar_date(self, data: str) -> datetime:
        nova_data = datetime.datetime(year=int(data.split("/")[2]),
                                      month=int(data.split("/")[1]),
                                      day=int(data.split("/")[0]))
        return nova_data
    
    def montar_excel(self: object, dados_lidos: list, coluna: list) -> None:
        workbook = excel.Workbook(self.nome_arquivo) 
        worksheet = workbook.add_worksheet() 
        
        worksheet.set_row(0,80)
        worksheet.insert_image('A1', f'{os.getcwd()}\\Img\\logo quadrada_.png')
        worksheet.set_column('A:F', 20)

        merge_format = workbook.add_format({
                                            'bold': 1,
                                            'border': 1,
                                            'align': 'center',
                                            'valign': 'vcenter',
                                            'fg_color': '#d8dada'
                                            ,'font_name':'Times New Roman'
                                            ,'font_size':18
                                            ,'font_color': '#001a33'})
        
        format_col = workbook.add_format({'bg_color': '#143352'
                                ,'font_color': 'white'
                                , "border": 1
                                ,'font_name':'Times New Roman'
                                ,'font_size':14
                                ,'align': 'center'})

        format_row = workbook.add_format({'font_name':'Times New Roman'
                                ,'font_size':13
                                ,'align': 'center'
                                ,"border": 1})
        format_data = workbook.add_format({'font_name':'Times New Roman'
                                ,'font_size':13
                                ,'align': 'center'
                                ,"border": 1})
        
        worksheet.merge_range('A1:F1', 'Cronograma Fadami Pay', merge_format)
        
        for col in range(len(coluna)):
            worksheet.write(1, col,coluna[col], format_col)
        
        for linha in range(len(dados_lidos)):
            for valor in range(len(dados_lidos[linha])):
                if valor >= 3 and valor <= 4:
                    dados_lidos[linha][valor] = self.formatar_date(dados_lidos[linha][valor])
                    data = dados_lidos[linha][valor].strftime('%d/%m/%Y')
                    worksheet.write((linha +2),valor,data,format_row)
                else:
                    worksheet.write((linha +2),valor,str(dados_lidos[linha][valor]),format_row)


        workbook.close()
        os.system(f'move {self.nome_arquivo} C:\\Users\\{os.getlogin()}\\Downloads\\')
        os.system(f'start excel {self.caminho_excel}\\{self.nome_arquivo}')
        