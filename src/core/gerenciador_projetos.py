from src.core.projeto import Projeto


class GerenciadorProjetos:
    def __init__(self):
        self.projetos = []

    def criar_projeto(self, nome, tipo):
        projeto = Projeto(nome, tipo)
        self.projetos.append(projeto)
        return projeto

    def buscar_por_id(self, id_projeto):
        for projeto in self.projetos:
            if projeto.id == id_projeto:
                return projeto

        return None