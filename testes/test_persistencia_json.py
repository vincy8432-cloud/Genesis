
import json

from src.core.projeto import Projeto
from src.core.gerenciador_projetos import GerenciadorProjetos
from src.persistencia.armazenamento_json import ArmazenamentoJSON


def test_salvar_e_carregar_projetos(tmp_path):
    arquivo = tmp_path / "projetos.json"
    armazenamento = ArmazenamentoJSON(arquivo)

    gerenciador = GerenciadorProjetos()
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
