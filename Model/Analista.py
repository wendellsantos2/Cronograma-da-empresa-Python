from Model import Modelo

class Analista(Modelo):
    
    def __init__(self: object, id_equipe:int = 0, nome_equipe: str = "", *, codigo: int, nome: str, email="", cd_status:int =1) -> None:
        super().__init__(codigo, nome, cd_status)
        self.id_equipe:int = id_equipe
        self.nome_equipe:str = nome_equipe
        self.email = email
    
    def montar_query_update(self:object, conteudo_pagina, equipes) -> None:
        id_equipe = tuple(filter(lambda equipe: equipe.nome == conteudo_pagina.box_equipe.currentText(), equipes))
                    
        return ("SPA_ANALISTAS", (self.codigo,
                                  conteudo_pagina.inpt_novo_nome.text(),
                                  id_equipe[0].codigo,
                                  conteudo_pagina.inpt_email.text()))