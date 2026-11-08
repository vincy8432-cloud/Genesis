import json
import os
import tempfile
from pathlib import Path
from uuid import UUID


class ErroPersistenciaArquivosJSON(Exception):
    """Erro relacionado ao armazenamento dos metadados dos arquivos."""


class ArmazenamentoArquivosJSON:

    def __init__(self, diretorio="dados/arquivos"):
        self.diretorio = Path(diretorio)

    def _caminho_arquivo(self, id_projeto):
        try:
            identificador = UUID(str(id_projeto))
        except (ValueError, TypeError, AttributeError) as erro:
            raise ValueError("ID de projeto inválido.") from erro

        return self.diretorio / f"{identificador}.json"

    def salvar(self, id_projeto, arquivos):
        caminho = self._caminho_arquivo(id_projeto)

        dados = []

        for arquivo in arquivos:
            dados.append({
                 "id": str(arquivo.id),
                 "nome_original": arquivo.nome_original,
                 "nome_armazenado": arquivo.nome_armazenado,
                 "caminho_relativo": arquivo.caminho_relativo.as_posix(),
                 "extensao": arquivo.extensao,
                 "tamanho": arquivo.tamanho,
                 "categoria": arquivo.categoria,
                 "data_importacao": (
                     arquivo.data_importacao.isoformat()
                 ),
                 "hash_sha256": arquivo.hash_sha256,
            })

        self.diretorio.mkdir(parents=True, exist_ok=True)

        caminho_temporario = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.diretorio,
                suffix=".tmp",
                delete=False,
            ) as temporario:
                caminho_temporario = Path(temporario.name)

                json.dump(
                    dados,
                    temporario,
                    ensure_ascii=False,
                    indent=4,
                )

                temporario.flush()
                os.fsync(temporario.fileno())

            os.replace(caminho_temporario, caminho)

        finally:
            if (
                caminho_temporario is not None
                and caminho_temporario.exists()
            ):
                caminho_temporario.unlink()

    def carregar(self, id_projeto):
        caminho = self._caminho_arquivo(id_projeto)

        if not caminho.exists():
            return []

        try:
            with caminho.open("r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

        except (json.JSONDecodeError, UnicodeDecodeError) as erro:
            raise ErroPersistenciaArquivosJSON(
                f"Arquivo de metadados inválido: {caminho}"
            ) from erro

        if not isinstance(dados, list):
            raise ErroPersistenciaArquivosJSON(
                "A estrutura dos metadados deve ser uma lista."
            )

        return dados
