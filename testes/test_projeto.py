import uuid
import pytest

from src.core.projeto import Projeto
from src.core.gerenciador_projetos import GerenciadorProjetos
from src.persistencia.armazenamento_json import ArmazenamentoJSON


@pytest.fixture
def gerenciador(tmp_path):
    armazenamento = ArmazenamentoJSON(
        tmp_path / "projetos.json"
    )

    return GerenciadorProjetos(
        armazenamento=armazenamento
    )

from src.persistencia.armazenamento_json import ArmazenamentoJSON
from src.core.projeto import Projeto
from src.core.gerenciador_projetos import GerenciadorProjetos


def test_criar_projeto():
    projeto = Projeto("Teste Genesis", "teste")

    assert projeto.nome == "Teste Genesis"
    assert projeto.tipo == "teste"
    assert projeto.id is not None


def test_projeto_inicia_ativo():
    projeto = Projeto("Teste Status", "teste")

    assert projeto.status == "ativo"


def test_projetos_diferentes_tem_ids_diferentes():
    projeto1 = Projeto("Projeto 1", "teste")
    projeto2 = Projeto("Projeto 2", "teste")

    assert projeto1.id != projeto2.id


def test_gerenciador_cria_e_armazena_projeto(gerenciador):
    projeto = gerenciador.criar_projeto("Livro Genesis", "livro")

    assert projeto.nome == "Livro Genesis"
    assert projeto.tipo == "livro"
    assert projeto in gerenciador.projetos


def test_gerenciador_busca_projeto_por_id(gerenciador):
    projeto = gerenciador.criar_projeto("Meu Livro", "livro")
    encontrado = gerenciador.buscar_por_id(projeto.id)

    assert encontrado is projeto


def test_gerenciador_retorna_none_para_id_inexistente(gerenciador):
    resultado = gerenciador.buscar_por_id(uuid.uuid4())

    assert resultado is None


def test_projeto_sem_nome_e_rejeitado():
    with pytest.raises(ValueError, match="O nome do projeto é obrigatório."):
        Projeto("", "livro")


def test_projeto_sem_tipo_e_rejeitado():
    with pytest.raises(ValueError, match="O tipo do projeto é obrigatório."):
        Projeto("Meu Livro", "")


def test_projeto_com_nome_apenas_de_espacos_e_rejeitado():
    with pytest.raises(ValueError, match="O nome do projeto é obrigatório."):
        Projeto("   ", "livro")


def test_projeto_com_tipo_apenas_de_espacos_e_rejeitado():
    with pytest.raises(ValueError, match="O tipo do projeto é obrigatório."):
        Projeto("Meu Livro", "   ")
