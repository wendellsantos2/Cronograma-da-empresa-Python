from Model import Modelo

class Projeto(Modelo):
    def __init__(self:object, codigo: str, nome: str, cd_status: int = 1) -> None:
        super().__init__(codigo, nome, cd_status)

    def montar_query_update(self:object, conteudo_pagina) -> None:
        return "SPA_PROJETO", (self.codigo,
                              conteudo_pagina.inpt_novo_nome.text())