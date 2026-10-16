
import uuid


class Projeto:
    def __init__(self, nome, tipo):
        if not nome or not nome.strip():
            raise ValueError("O nome do projeto é obrigatório.")

        if not tipo or not tipo.strip():
            raise ValueError("O tipo do projeto é obrigatório.")

        self.id = uuid.uuid4()
        self.nome = nome.strip()
        self.tipo = tipo.strip()
        self.status = "ativo"
