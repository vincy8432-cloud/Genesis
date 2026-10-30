
import json
import os
import tempfile

from pathlib import Path
from uuid import UUID

from src.core.projeto import Projeto


class ErroPersistenciaJSON(Exception):
    """Erro relacionado à leitura ou validação dos dados JSON."""


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

        # Valida os dados antes de iniciar a gravação.
        self._validar_dados(dados)

        self.caminho_arquivo.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        arquivo_temporario = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.caminho_arquivo.parent,
                prefix=f".{self.caminho_arquivo.name}.",
                suffix=".tmp",
                delete=False,
            ) as arquivo:
                arquivo_temporario = Path(arquivo.name)

                json.dump(
                    dados,
                    arquivo,
                    ensure_ascii=False,
                    indent=4,
                )

                arquivo.flush()
                os.fsync(arquivo.fileno())

            # Substitui o arquivo original somente após
            # concluir a gravação do arquivo temporário.
            arquivo_temporario.replace(self.caminho_arquivo)

        finally:
            if (
                arquivo_temporario is not None
                and arquivo_temporario.exists()
            ):
                arquivo_temporario.unlink()

    def carregar(self):
        if not self.caminho_arquivo.exists():
            return []

        try:
            with self.caminho_arquivo.open(
                "r",
                encoding="utf-8",
            ) as arquivo:
                dados = json.load(arquivo)

        except (json.JSONDecodeError, UnicodeDecodeError) as erro:
            raise ErroPersistenciaJSON(
                f"Arquivo JSON corrompido: {self.caminho_arquivo}"
            ) from erro

        self._validar_dados(dados)

        projetos = []

        for item in dados:
            projeto = Projeto(
                item["nome"],
                item["tipo"],
            )

            projeto.id = UUID(item["id"])
            projeto.status = item["status"]

            projetos.append(projeto)

        return projetos

    @staticmethod
    def _validar_dados(dados):
        if not isinstance(dados, list):
            raise ErroPersistenciaJSON(
                "A estrutura principal do JSON deve ser uma lista."
            )

        ids_encontrados = set()

        campos = ("id", "nome", "tipo", "status")

        for indice, item in enumerate(dados):
            if not isinstance(item, dict):
                raise ErroPersistenciaJSON(
                    f"O projeto na posição {indice} deve ser um objeto."
                )

            for campo in campos:
                if campo not in item:
                    raise ErroPersistenciaJSON(
                        f"Campo obrigatório ausente: '{campo}' "
                        f"no projeto {indice}."
                    )

                if not isinstance(item[campo], str):
                    raise ErroPersistenciaJSON(
                        f"O campo '{campo}' do projeto {indice} "
                        "deve ser texto."
                    )

                if not item[campo].strip():
                    raise ErroPersistenciaJSON(
                        f"O campo '{campo}' do projeto {indice} "
                        "não pode estar vazio."
                    )

            try:
                id_projeto = UUID(item["id"])
            except ValueError as erro:
                raise ErroPersistenciaJSON(
                    f"UUID inválido no projeto {indice}."
                ) from erro

            if id_projeto in ids_encontrados:
                raise ErroPersistenciaJSON(
                    f"ID duplicado no projeto {indice}: {id_projeto}"
                )

            ids_encontrados.add(id_projeto)
