
import json
from pathlib import Path
from uuid import UUID

from src.core.projeto import Projeto


class ArmazenamentoJSON:
    def __init__(self, caminho_arquivo):
        self.caminho_arquivo = Path(caminho_arquivo)

    def salvar(self, projetos):
        dados = [
            {
                "id": str(projeto.id),
                "nome": projeto.nome,
                "tipo": projeto.tipo,
                "status": projeto.status,
            }
            for projeto in projetos
        ]

        self.caminho_arquivo.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.caminho_arquivo.open(
            "w",
            encoding="utf-8",
        ) as arquivo:
            json.dump(
                dados,
                arquivo,
                ensure_ascii=False,
                indent=4,
            )

    def carregar(self):
        if not self.caminho_arquivo.exists():
            return []

        with self.caminho_arquivo.open(
            "r",
            encoding="utf-8",
        ) as arquivo:
            dados = json.load(arquivo)

        projetos = []

        for item in dados:
            projeto = Projeto(item["nome"], item["tipo"])
            projeto.id = UUID(item["id"])
            projeto.status = item["status"]
            projetos.append(projeto)

        return projetos
