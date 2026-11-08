import json
import uuid

import pytest

from src.core.arquivo_projeto import ArquivoProjeto
from src.persistencia.armazenamento_arquivos_json import (
    ArmazenamentoArquivosJSON,
    ErroPersistenciaArquivosJSON,
)


def test_salva_e_carrega_metadados(tmp_path):
    origem = tmp_path / "livro.txt"
    origem.write_text("Conteúdo do Genesis", encoding="utf-8")

    projeto_id = uuid.uuid4()
    armazenamento = ArmazenamentoArquivosJSON(
        tmp_path / "dados" / "arquivos"
    )

    arquivo = ArquivoProjeto(origem, "documento")

    armazenamento.salvar(projeto_id, [arquivo])
    dados = armazenamento.carregar(projeto_id)

    assert len(dados) == 1
    assert dados[0]["id"] == str(arquivo.id)
    assert dados[0]["nome_original"] == "livro.txt"
    assert dados[0]["extensao"] == ".txt"
    assert dados[0]["tamanho"] == arquivo.tamanho
    assert dados[0]["categoria"] == "documento"
    assert dados[0]["hash_sha256"] == arquivo.hash_sha256
    assert dados[0]["nome_armazenado"] == arquivo.nome_armazenado

    assert (
        dados[0]["caminho_relativo"]
        == arquivo.caminho_relativo.as_posix()
    )
    
def test_carrega_lista_vazia_quando_nao_existe_registro(tmp_path):
    armazenamento = ArmazenamentoArquivosJSON(tmp_path)

    assert armazenamento.carregar(uuid.uuid4()) == []


def test_isola_metadados_por_projeto(tmp_path):
    armazenamento = ArmazenamentoArquivosJSON(tmp_path)

    primeiro_id = uuid.uuid4()
    segundo_id = uuid.uuid4()

    origem = tmp_path / "teste.txt"
    origem.write_text("Genesis", encoding="utf-8")

    arquivo = ArquivoProjeto(origem)

    armazenamento.salvar(primeiro_id, [arquivo])

    assert len(armazenamento.carregar(primeiro_id)) == 1
    assert armazenamento.carregar(segundo_id) == []


def test_rejeita_id_de_projeto_invalido(tmp_path):
    armazenamento = ArmazenamentoArquivosJSON(tmp_path)

    with pytest.raises(ValueError, match="ID de projeto inválido"):
        armazenamento.carregar("id-invalido")


def test_rejeita_json_corrompido(tmp_path):
    armazenamento = ArmazenamentoArquivosJSON(tmp_path)
    projeto_id = uuid.uuid4()

    caminho = armazenamento.diretorio / f"{projeto_id}.json"
    caminho.write_text("{json inválido", encoding="utf-8")

    with pytest.raises(ErroPersistenciaArquivosJSON):
        armazenamento.carregar(projeto_id)


def test_rejeita_estrutura_json_invalida(tmp_path):
    armazenamento = ArmazenamentoArquivosJSON(tmp_path)
    projeto_id = uuid.uuid4()

    caminho = armazenamento.diretorio / f"{projeto_id}.json"
    caminho.write_text(
        json.dumps({"arquivo": "teste.txt"}),
        encoding="utf-8",
    )

    with pytest.raises(ErroPersistenciaArquivosJSON):
        armazenamento.carregar(projeto_id)


def test_salva_lista_vazia(tmp_path):
    armazenamento = ArmazenamentoArquivosJSON(tmp_path)
    projeto_id = uuid.uuid4()

    armazenamento.salvar(projeto_id, [])

    assert armazenamento.carregar(projeto_id) == []


def test_reconstrui_objeto_arquivo_a_partir_dos_metadados(tmp_path):
    origem = tmp_path / "livro.txt"
    origem.write_text("Conteúdo do Genesis", encoding="utf-8")

    projeto_id = uuid.uuid4()

    armazenamento = ArmazenamentoArquivosJSON(
        tmp_path / "dados" / "arquivos"
    )

    original = ArquivoProjeto(origem, "documento")

    armazenamento.salvar(projeto_id, [original])

    dados = armazenamento.carregar(projeto_id)
    reconstruido = ArquivoProjeto.reconstruir(dados[0])

    assert reconstruido.id == original.id
    assert reconstruido.nome_original == original.nome_original
    assert reconstruido.nome_armazenado == original.nome_armazenado
    assert reconstruido.caminho_relativo == original.caminho_relativo
    assert reconstruido.extensao == original.extensao
    assert reconstruido.tamanho == original.tamanho
    assert reconstruido.categoria == original.categoria
    assert reconstruido.hash_sha256 == original.hash_sha256
    assert reconstruido.data_importacao == original.data_importacao
