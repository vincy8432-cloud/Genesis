import shutil
from pathlib import Path


class GerenciadorDiretorios:

    def __init__(self, diretorio_base="projetos"):
        self.diretorio_base = Path(diretorio_base)

    def criar_estrutura(self, projeto):
        diretorio_projeto = (
            self.diretorio_base / str(projeto.id)
        )

        diretorios = [
            diretorio_projeto / "arquivos",
            diretorio_projeto / "materiais",
            diretorio_projeto / "resultados",
        ]

        for diretorio in diretorios:
            diretorio.mkdir(
                parents=True,
                exist_ok=True,
            )

        return diretorio_projeto

    def remover_estrutura(self, projeto):
        diretorio_projeto = (
            self.diretorio_base / str(projeto.id)
        )

        shutil.rmtree(
            diretorio_projeto,
            ignore_errors=True,
        )