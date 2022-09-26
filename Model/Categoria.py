from Model import Modelo

class Categoria(Modelo):
    
    def __init__(self, codigo, nome):
        super().__init__(codigo=codigo, nome=nome)

