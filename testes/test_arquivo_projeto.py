import hashlib
import pytest

from src.core.arquivo_projeto import ArquivoProjeto


def test_cria_arquivo_com_metadados(tmp_path):
    origem = tmp_path / "livro.txt"
    conteudo = "Conteúdo do livro"
    origem.write_text(conteudo, encoding="utf-8")

    arquivo = ArquivoProjeto(origem, "documento")

    assert arquivo.nome_original == "livro.txt"
    assert arquivo.extensao == ".txt"
    assert arquivo.tamanho == len(conteudo.encode("utf-8"))
    assert arquivo.categoria == "documento"
    assert len(str(arquivo.id)) == 36
    assert arquivo.data_importacao is not None


def test_calcula_hash_sha256(tmp_path):
    origem = tmp_path / "teste.txt"
    conteudo = b"Genesis"
    origem.write_bytes(conteudo)

    arquivo = ArquivoProjeto(origem)

    hash_esperado = hashlib.sha256(conteudo).hexdigest()

    assert arquivo.hash_sha256 == hash_esperado


def test_gera_ids_diferentes(tmp_path):
    origem = tmp_path / "teste.txt"
    origem.write_text("Genesis", encoding="utf-8")

    primeiro = ArquivoProjeto(origem)
    segundo = ArquivoProjeto(origem)

    assert primeiro.id != segundo.id


def test_rejeita_arquivo_inexistente(tmp_path):
    origem = tmp_path / "inexistente.txt"

    with pytest.raises(FileNotFoundError):
        ArquivoProjeto(origem)


def test_rejeita_diretorio_como_arquivo(tmp_path):
    with pytest.raises(ValueError):
        ArquivoProjeto(tmp_path)


def test_rejeita_categoria_vazia(tmp_path):
    origem = tmp_path / "teste.txt"
    origem.write_text("Genesis", encoding="utf-8")

    with pytest.raises(ValueError):
        ArquivoProjeto(origem, "   ")
