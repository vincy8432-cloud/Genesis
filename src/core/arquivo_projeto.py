import uuid
import hashlib
from pathlib import Path
from datetime import datetime, timezone


class ArquivoProjeto:
    def __init__(self, caminho_origem, categoria="arquivo"):
        caminho = Path(caminho_origem)

        if not caminho.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {caminho}"
            )

        if not caminho.is_file():
            raise ValueError(
                "O caminho informado não corresponde a um arquivo."
            )

        if not categoria or not categoria.strip():
            raise ValueError("A categoria do arquivo é obrigatória.")

        self.id = uuid.uuid4()
        self.nome_original = caminho.name
        self.extensao = caminho.suffix.lower()

        self.nome_armazenado = f"{self.id}{self.extensao}"
        self.caminho_relativo = (
            Path("arquivos") / self.nome_armazenado
        )
        self.tamanho = caminho.stat().st_size
        self.categoria = categoria.strip()
        self.data_importacao = datetime.now(timezone.utc)
        self.hash_sha256 = self._calcular_hash(caminho)
    @classmethod
    def reconstruir(cls, dados):
        arquivo = cls.__new__(cls)

        arquivo.id = uuid.UUID(dados["id"])
        arquivo.nome_original = dados["nome_original"]
        arquivo.nome_armazenado = dados["nome_armazenado"]
        arquivo.caminho_relativo = Path(
            dados["caminho_relativo"]
        )
        arquivo.extensao = dados["extensao"]
        arquivo.tamanho = dados["tamanho"]
        arquivo.categoria = dados["categoria"]
        arquivo.data_importacao = datetime.fromisoformat(
            dados["data_importacao"]
        )
        arquivo.hash_sha256 = dados["hash_sha256"]
        return arquivo
    @staticmethod
    def _calcular_hash(caminho):
        sha256 = hashlib.sha256()

        with open(caminho, "rb") as arquivo:
            for bloco in iter(
                lambda: arquivo.read(1024 * 1024),
                b"",
            ):
                sha256.update(bloco)

        return sha256.hexdigest()
