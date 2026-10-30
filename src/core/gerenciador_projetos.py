
from src.core.projeto import Projeto
from src.persistencia.armazenamento_json import ArmazenamentoJSON


class GerenciadorProjetos:
    def __init__(self, armazenamento=None):
        self.armazenamento = armazenamento or ArmazenamentoJSON(
            "dados/projetos.json"
        )

        self.projetos = self.armazenamento.carregar()

    def criar_projeto(self, nome, tipo):
        projeto = Projeto(nome, tipo)
        self.projetos.append(projeto)
        self.armazenamento.salvar(self.projetos)
        return projeto

    def buscar_por_id(self, id_projeto):
        for projeto in self.projetos:
            if projeto.id == id_projeto:
                return projeto

        return None
