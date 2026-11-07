import uuid


class Projeto:
    STATUS_ATIVO = "ativo"
    STATUS_ARQUIVADO = "arquivado"

    STATUS_PERMITIDOS = (
        STATUS_ATIVO,
        STATUS_ARQUIVADO,
    )

    def __init__(self, nome, tipo):
        if not nome or not nome.strip():
            raise ValueError("O nome do projeto é obrigatório.")

        if not tipo or not tipo.strip():
            raise ValueError("O tipo do projeto é obrigatório.")

        self.id = uuid.uuid4()
        self.nome = nome.strip()
        self.tipo = tipo.strip()
        self._status = self.STATUS_ATIVO

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, valor):
        if valor not in self.STATUS_PERMITIDOS:
            raise ValueError(
                f"Status inválido: {valor}. "
                f"Valores permitidos: {self.STATUS_PERMITIDOS}"
            )

        self._status = valor