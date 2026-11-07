
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


    def atualizar_projeto(self, id_projeto, nome=None, tipo=None):
        for indice, projeto_atual in enumerate(self.projetos):
            if projeto_atual.id == id_projeto:

                novo_nome = (
                    projeto_atual.nome if nome is None else nome
                )

                novo_tipo = (
                    projeto_atual.tipo if tipo is None else tipo
                )

                # Valida os novos dados sem modificar o projeto original.
                projeto_atualizado = Projeto(
                    novo_nome,
                    novo_tipo,
                )

                # Preserva a identidade e o status do projeto.
                projeto_atualizado.id = projeto_atual.id
                projeto_atualizado.status = projeto_atual.status

                # Prepara uma lista independente.
                projetos_atualizados = self.projetos.copy()
                projetos_atualizados[indice] = projeto_atualizado

                # Persiste antes de modificar a memória.
                self.armazenamento.salvar(projetos_atualizados)

                # Atualiza o objeto original somente após o sucesso.
                projeto_atual.nome = projeto_atualizado.nome
                projeto_atual.tipo = projeto_atualizado.tipo

                return projeto_atual

        return None

        def remover_projeto(self, id_projeto):
            for indice, projeto in enumerate(self.projetos):
                if projeto.id == id_projeto:

                    # Prepara uma lista sem o projeto selecionado.
                    projetos_atualizados = self.projetos.copy()
                    projeto_removido = projetos_atualizados.pop(indice)

                    # Persiste antes de modificar a memória.
                    self.armazenamento.salvar(projetos_atualizados)

                    # Atualiza a lista original somente após o sucesso.
                    self.projetos.pop(indice)

                    return projeto_removido

            return None

    def remover_projeto(self, id_projeto):
        for indice, projeto in enumerate(self.projetos):
            if projeto.id == id_projeto:

                # Prepara uma lista sem o projeto selecionado.
                projetos_atualizados = self.projetos.copy()
                projeto_removido = projetos_atualizados.pop(indice)

                # Persiste antes de modificar a memória.
                self.armazenamento.salvar(projetos_atualizados)

                # Atualiza a lista original somente após o sucesso.
                self.projetos.pop(indice)

                return projeto_removido

        return None

    def buscar_por_id(self, id_projeto):
        for projeto in self.projetos:
            if projeto.id == id_projeto:
                return projeto

        return None
