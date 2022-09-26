from Controller import ConnectionDB, Log


class Modelo():
    
    def __init__(self, codigo: str, nome:str, cd_status: int = 0) -> None:
        # Código GENÉRICO PARA CLASSES.
        self.codigo = codigo
        self.nome = nome
        self.cd_status = cd_status
    
    def montar_query(self: object) -> str:
        pass
    