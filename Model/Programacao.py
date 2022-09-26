from Modelo import Modelo

class Categoria(Modelo):
    
    def __init__(self, codigoCategoria, nomeCategoria, codigoProjeto, codigoAnalista, dataInicio, dataFim):
        super().__init__(codigo=codigoCategoria, nome=nomeCategoria)
        self.codigoProjeto = codigoProjeto
        self.codigoAnalista = codigoAnalista
        self.dataInicio = dataInicio
        self.dataInicio = dataFim
        
