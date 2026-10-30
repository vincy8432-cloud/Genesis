
from src.core.projeto import Projeto
from src.persistencia.armazenamento_json import ArmazenamentoJSON


class GerenciadorProjetos:
    def __init__(self, armazenamento=None):
        if armazenamento is None:
            armazenamento = ArmazenamentoJSON(
                "dados/projetos.json"
            )

        self.armazenamento = armazenamento
        self.projetos = self.armazenamento.carregar()

    def criar_projeto(self, nome, tipo):
        projeto = Projeto(nome, tipo)

        # Prepara a nova lista sem modificar a lista atual.
        projetos_atualizados = self.projetos + [projeto]

        # Primeiro confirma a gravação.
        self.armazenamento.salvar(projetos_atualizados)

        # Só atualiza a memória depois do sucesso.
        self.projetos.append(projeto)

        return projeto

    def buscar_por_id(self, id_projeto):
        for projeto in self.projetos:
            if projeto.id == id_projeto:
                return projeto

        return None
