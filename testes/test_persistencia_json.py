import pytest

from src.persistencia.armazenamento_json import (
    ArmazenamentoJSON,
    ErroPersistenciaJSON,
)

import json

from src.core.projeto import Projeto
from src.core.gerenciador_projetos import GerenciadorProjetos
from src.persistencia.armazenamento_json import ArmazenamentoJSON
from pathlib import Path

def test_salvar_e_carregar_projetos(tmp_path):
    arquivo = tmp_path / "projetos.json"
    armazenamento = ArmazenamentoJSON(arquivo)

    gerenciador = GerenciadorProjetos(
        armazenamento=armazenamento
    )

    projeto = gerenciador.criar_projeto(
        "O Último Segundo Antes...",
        "livro"
    )

    armazenamento.salvar(gerenciador.projetos)
    projetos_carregados = armazenamento.carregar()

    assert len(projetos_carregados) == 1
    assert projetos_carregados[0].id == projeto.id
    assert projetos_carregados[0].nome == projeto.nome
    assert projetos_carregados[0].tipo == projeto.tipo
    assert projetos_carregados[0].status == projeto.status


def test_arquivo_json_contem_dados_dos_projetos(tmp_path):
    arquivo = tmp_path / "projetos.json"
    armazenamento = ArmazenamentoJSON(arquivo)

    projeto = Projeto("Projeto de teste", "musica")
    armazenamento.salvar([projeto])

    dados = json.loads(arquivo.read_text(encoding="utf-8"))

    assert len(dados) == 1
    assert dados[0]["nome"] == "Projeto de teste"
    assert dados[0]["tipo"] == "musica"


def test_carregar_arquivo_inexistente_retorna_lista_vazia(tmp_path):
    armazenamento = ArmazenamentoJSON(
        tmp_path / "nao_existe.json"
    )

    assert armazenamento.carregar() == []


def test_gerenciador_carrega_projetos_salvos_ao_iniciar(tmp_path):
    arquivo = tmp_path / "projetos.json"
    armazenamento = ArmazenamentoJSON(arquivo)

    projeto_original = Projeto("Genesis", "livro")
    armazenamento.salvar([projeto_original])

    gerenciador = GerenciadorProjetos(
        armazenamento=armazenamento
    )

    assert len(gerenciador.projetos) == 1
    assert gerenciador.projetos[0].id == projeto_original.id
    assert gerenciador.projetos[0].nome == "Genesis"


def test_gerenciador_salva_projeto_criado(tmp_path):
    arquivo = tmp_path / "projetos.json"
    armazenamento = ArmazenamentoJSON(arquivo)

    gerenciador = GerenciadorProjetos(
        armazenamento=armazenamento
    )

    projeto = gerenciador.criar_projeto("Meu projeto", "teste")

    projetos_salvos = armazenamento.carregar()

    assert len(projetos_salvos) == 1
    assert projetos_salvos[0].id == projeto.id
    assert projetos_salvos[0].nome == "Meu projeto"


def test_carregar_json_corrompido(tmp_path):
    arquivo = tmp_path / "projetos.json"
    arquivo.write_text("{json invalido", encoding="utf-8")

    armazenamento = ArmazenamentoJSON(arquivo)

    with pytest.raises(ErroPersistenciaJSON):
        armazenamento.carregar()


def test_carregar_estrutura_json_invalida(tmp_path):
    arquivo = tmp_path / "projetos.json"
    arquivo.write_text('{"projetos": []}', encoding="utf-8")

    armazenamento = ArmazenamentoJSON(arquivo)

    with pytest.raises(ErroPersistenciaJSON):
        armazenamento.carregar()


def test_carregar_projeto_com_uuid_invalido(tmp_path):
    arquivo = tmp_path / "projetos.json"

    dados = [{
        "id": "uuid-invalido",
        "nome": "Projeto teste",
        "tipo": "livro",
        "status": "ativo",
    }]

    arquivo.write_text(
        json.dumps(dados),
        encoding="utf-8",
    )

    armazenamento = ArmazenamentoJSON(arquivo)

    with pytest.raises(ErroPersistenciaJSON):
        armazenamento.carregar()


def test_carregar_projeto_com_campo_ausente(tmp_path):
    arquivo = tmp_path / "projetos.json"

    dados = [{
        "id": "c667904d-60cc-496e-9414-4a163a29e1ed",
        "nome": "Projeto teste",
        "tipo": "livro",
    }]

    arquivo.write_text(
        json.dumps(dados),
        encoding="utf-8",
    )

    armazenamento = ArmazenamentoJSON(arquivo)

    with pytest.raises(ErroPersistenciaJSON):
        armazenamento.carregar()


def test_salvar_dados_invalidos_preserva_arquivo_original(tmp_path):
    arquivo = tmp_path / "projetos.json"
    conteudo_original = '[{"dados": "originais"}]'

    arquivo.write_text(
        conteudo_original,
        encoding="utf-8",
    )

    projeto = Projeto("Projeto teste", "livro")
    projeto.nome = ""

    armazenamento = ArmazenamentoJSON(arquivo)

    with pytest.raises(ErroPersistenciaJSON):
        armazenamento.salvar([projeto])

    assert arquivo.read_text(encoding="utf-8") == conteudo_original


def test_nao_permite_ids_duplicados_no_json(tmp_path):
    arquivo = tmp_path / "projetos.json"

    id_compartilhado = "c667904d-60cc-496e-9414-4a163a29e1ed"

    dados = [
        {
            "id": id_compartilhado,
            "nome": "Projeto A",
            "tipo": "livro",
            "status": "ativo",
        },
        {
            "id": id_compartilhado,
            "nome": "Projeto B",
            "tipo": "musica",
            "status": "ativo",
        },
    ]

    arquivo.write_text(
        json.dumps(dados),
        encoding="utf-8",
    )

    armazenamento = ArmazenamentoJSON(arquivo)

    with pytest.raises(ErroPersistenciaJSON):
        armazenamento.carregar()


def test_falha_na_substituicao_preserva_arquivo_original(
    tmp_path,
    monkeypatch,
):
    arquivo = tmp_path / "projetos.json"

    conteudo_original = '[{"dados": "originais"}]'

    arquivo.write_text(
        conteudo_original,
        encoding="utf-8",
    )

    armazenamento = ArmazenamentoJSON(arquivo)

    projeto = Projeto("Projeto teste", "livro")

    def falhar_substituicao(self, destino):
        raise OSError("Falha simulada na substituicao.")

    monkeypatch.setattr(
        Path,
        "replace",
        falhar_substituicao,
    )

    with pytest.raises(OSError, match="Falha simulada"):
        armazenamento.salvar([projeto])

    assert arquivo.read_text(encoding="utf-8") == conteudo_original

    temporarios = list(tmp_path.glob(".*.tmp"))

    assert temporarios == []


def test_gerenciador_nao_adiciona_projeto_quando_salvamento_falha(
    tmp_path,
    monkeypatch,
):
    arquivo = tmp_path / "projetos.json"
    armazenamento = ArmazenamentoJSON(arquivo)

    projeto_existente = Projeto("Projeto existente", "livro")
    armazenamento.salvar([projeto_existente])

    gerenciador = GerenciadorProjetos(
        armazenamento=armazenamento
    )

    conteudo_original = arquivo.read_text(encoding="utf-8")

    def falhar_salvamento(projetos):
        raise OSError("Falha simulada na gravacao.")

    monkeypatch.setattr(
        armazenamento,
        "salvar",
        falhar_salvamento,
    )

    with pytest.raises(OSError, match="Falha simulada"):
        gerenciador.criar_projeto(
            "Projeto novo",
            "musica",
        )

    assert len(gerenciador.projetos) == 1

    assert gerenciador.projetos[0].id == projeto_existente.id

    assert arquivo.read_text(encoding="utf-8") == conteudo_original
