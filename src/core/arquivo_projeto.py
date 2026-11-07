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
        self.tamanho = caminho.stat().st_size
        self.categoria = categoria.strip()
        self.data_importacao = datetime.now(timezone.utc)
        self.hash_sha256 = self._calcular_hash(caminho)

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
