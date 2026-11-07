
from src.core.projeto import Projeto
from src.persistencia.armazenamento_json import ArmazenamentoJSON
from src.estrutura.gerenciador_diretorios import GerenciadorDiretorios


class GerenciadorProjetos:
    def __init__(self, armazenamento=None, gerenciador_diretorios=None):
        if armazenamento is None:
            armazenamento = ArmazenamentoJSON(
                "dados/projetos.json"
            )

        if gerenciador_diretorios is None:
            gerenciador_diretorios = GerenciadorDiretorios()

        self.armazenamento = armazenamento
        self.gerenciador_diretorios = gerenciador_diretorios
        self.projetos = self.armazenamento.carregar()

        # Recupera as estruturas dos projetos cadastrados.
        for projeto in self.projetos:
            self.gerenciador_diretorios.criar_estrutura(projeto)

    def criar_projeto(self, nome, tipo):
        projeto = Projeto(nome, tipo)

        projetos_atualizados = self.projetos + [projeto]

        diretorio_projeto = (
            self.gerenciador_diretorios.diretorio_base
            / str(projeto.id)
        )

        estrutura_existia = diretorio_projeto.exists()

        try:
            # Cria a estrutura de diretórios.
            self.gerenciador_diretorios.criar_estrutura(projeto)

            # Persiste os dados do projeto.
            self.armazenamento.salvar(projetos_atualizados)

        except Exception:
            # Remove a estrutura somente se ela foi criada agora.
            if not estrutura_existia:
                self.gerenciador_diretorios.remover_estrutura(projeto)

            raise

        # Atualiza a memória somente após o sucesso.
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

    def arquivar_projeto(self, id_projeto):
        return self._alterar_status(
            id_projeto,
            Projeto.STATUS_ARQUIVADO,
        )

    def reativar_projeto(self, id_projeto):
        return self._alterar_status(
            id_projeto,
            Projeto.STATUS_ATIVO,
        )

    def _alterar_status(self, id_projeto, novo_status):
        for indice, projeto in enumerate(self.projetos):
            if projeto.id == id_projeto:

                if projeto.status == novo_status:
                    return projeto

                projeto_atualizado = Projeto(
                    projeto.nome,
                    projeto.tipo,
                )

                projeto_atualizado.id = projeto.id
                projeto_atualizado.status = novo_status

                projetos_atualizados = self.projetos.copy()
                projetos_atualizados[indice] = projeto_atualizado

                self.armazenamento.salvar(projetos_atualizados)

                projeto.status = novo_status

                return projeto

        return None

    def listar_por_status(self, status):
        if status not in Projeto.STATUS_PERMITIDOS:
            raise ValueError(
                f"Status inválido: {status}. "
                f"Valores permitidos: {Projeto.STATUS_PERMITIDOS}"
            )

        return [
            projeto
            for projeto in self.projetos
            if projeto.status == status
        ]

    def buscar_por_id(self, id_projeto):
        for projeto in self.projetos:
            if projeto.id == id_projeto:
                return projeto

        return None