import uuid
import pytest

from src.core.projeto import Projeto
from src.core.gerenciador_projetos import GerenciadorProjetos
from src.persistencia.armazenamento_json import ArmazenamentoJSON
from src.estrutura.gerenciador_diretorios import GerenciadorDiretorios

@pytest.fixture
def gerenciador(tmp_path):
    armazenamento = ArmazenamentoJSON(
        tmp_path / "projetos.json"
    )

    gerenciador_diretorios = GerenciadorDiretorios(
        tmp_path / "projetos"
    )

    return GerenciadorProjetos(
        armazenamento=armazenamento,
        gerenciador_diretorios=gerenciador_diretorios,
    )

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


def test_gerenciador_atualiza_projeto(gerenciador):
    projeto = gerenciador.criar_projeto(
        "Meu Livro",
        "livro",
    )

    id_original = projeto.id

    projeto_atualizado = gerenciador.atualizar_projeto(
        id_original,
        nome="O Último Segundo Antes...",
        tipo="publicacao",
    )

    assert projeto_atualizado is projeto
    assert projeto_atualizado.id == id_original
    assert projeto_atualizado.nome == "O Último Segundo Antes..."
    assert projeto_atualizado.tipo == "publicacao"
    assert projeto_atualizado.status == "ativo"


def test_gerenciador_atualiza_apenas_nome(gerenciador):
    projeto = gerenciador.criar_projeto(
        "Meu Livro",
        "livro",
    )

    projeto_atualizado = gerenciador.atualizar_projeto(
        projeto.id,
        nome="Novo Nome",
    )

    assert projeto_atualizado.nome == "Novo Nome"
    assert projeto_atualizado.tipo == "livro"


def test_gerenciador_nao_atualiza_projeto_inexistente(gerenciador):
    id_inexistente = uuid.uuid4()

    resultado = gerenciador.atualizar_projeto(
        id_inexistente,
        nome="Projeto inexistente",
    )

    assert resultado is None
    assert gerenciador.projetos == []


def test_gerenciador_preserva_projeto_se_atualizacao_falhar(
    gerenciador,
    monkeypatch,
):
    projeto = gerenciador.criar_projeto(
        "Projeto original",
        "livro",
    )

    conteudo_original = (
        gerenciador.armazenamento.caminho_arquivo.read_text(
            encoding="utf-8"
        )
    )

    def falhar_salvamento(projetos):
        raise OSError("Falha simulada na gravacao.")

    monkeypatch.setattr(
        gerenciador.armazenamento,
        "salvar",
        falhar_salvamento,
    )

    with pytest.raises(OSError, match="Falha simulada"):
        gerenciador.atualizar_projeto(
            projeto.id,
            nome="Novo nome",
        )

    assert projeto.nome == "Projeto original"
    assert projeto.tipo == "livro"
    assert gerenciador.buscar_por_id(projeto.id) is projeto

    conteudo_atual = (
        gerenciador.armazenamento.caminho_arquivo.read_text(
            encoding="utf-8"
        )
    )

    assert conteudo_atual == conteudo_original

def test_remover_projeto_remove_e_persiste(gerenciador):
    projeto = gerenciador.criar_projeto(
        "Projeto para Remover",
        "livro",
    )

    id_projeto = projeto.id

    removido = gerenciador.remover_projeto(id_projeto)

    assert removido is projeto
    assert gerenciador.buscar_por_id(id_projeto) is None
    assert projeto not in gerenciador.projetos

    # Confirma que a remoção foi persistida.
    gerenciador_recarregado = GerenciadorProjetos(
        armazenamento=gerenciador.armazenamento
    )

    assert gerenciador_recarregado.buscar_por_id(id_projeto) is None


def test_remover_projeto_inexistente_retorna_none(gerenciador):
    from uuid import uuid4

    quantidade_anterior = len(gerenciador.projetos)

    resultado = gerenciador.remover_projeto(uuid4())

    assert resultado is None
    assert len(gerenciador.projetos) == quantidade_anterior


def test_falha_ao_remover_projeto_preserva_memoria_e_arquivo(
    gerenciador,
    monkeypatch,
):
    projeto = gerenciador.criar_projeto(
        "Projeto Protegido",
        "livro",
    )

    arquivo = gerenciador.armazenamento.caminho_arquivo
    conteudo_anterior = arquivo.read_bytes()

    def falhar_salvamento(projetos):
        raise OSError("Falha simulada no armazenamento.")

    monkeypatch.setattr(
        gerenciador.armazenamento,
        "salvar",
        falhar_salvamento,
    )

    import pytest

    with pytest.raises(OSError):
        gerenciador.remover_projeto(projeto.id)

    assert gerenciador.buscar_por_id(projeto.id) is projeto
    assert arquivo.read_bytes() == conteudo_anterior

def test_arquivar_projeto(gerenciador):
    projeto = gerenciador.criar_projeto(
        "Projeto para Arquivar",
        "livro",
    )

    id_original = projeto.id

    resultado = gerenciador.arquivar_projeto(id_original)

    assert resultado is projeto
    assert projeto.id == id_original
    assert projeto.status == Projeto.STATUS_ARQUIVADO

    # Confirma a persistência.
    recarregado = GerenciadorProjetos(
        armazenamento=gerenciador.armazenamento
    )

    projeto_recarregado = recarregado.buscar_por_id(id_original)

    assert projeto_recarregado.status == Projeto.STATUS_ARQUIVADO


def test_reativar_projeto(gerenciador):
    projeto = gerenciador.criar_projeto(
        "Projeto Arquivado",
        "livro",
    )

    gerenciador.arquivar_projeto(projeto.id)

    resultado = gerenciador.reativar_projeto(projeto.id)

    assert resultado is projeto
    assert projeto.status == Projeto.STATUS_ATIVO


def test_arquivar_projeto_inexistente(gerenciador):
    from uuid import uuid4

    resultado = gerenciador.arquivar_projeto(uuid4())

    assert resultado is None


def test_falha_ao_arquivar_preserva_status(
    gerenciador,
    monkeypatch,
):
    projeto = gerenciador.criar_projeto(
        "Projeto Protegido",
        "livro",
    )

    conteudo_anterior = (
        gerenciador.armazenamento.caminho_arquivo.read_bytes()
    )

    def falhar_salvamento(projetos):
        raise OSError("Falha simulada no armazenamento.")

    monkeypatch.setattr(
        gerenciador.armazenamento,
        "salvar",
        falhar_salvamento,
    )

    import pytest

    with pytest.raises(OSError):
        gerenciador.arquivar_projeto(projeto.id)

    assert projeto.status == Projeto.STATUS_ATIVO

    assert (
        gerenciador.armazenamento.caminho_arquivo.read_bytes()
        == conteudo_anterior
    )

def test_listar_projetos_ativos(gerenciador):
    projeto1 = gerenciador.criar_projeto("Livro 1", "livro")
    projeto2 = gerenciador.criar_projeto("Livro 2", "livro")

    gerenciador.arquivar_projeto(projeto2.id)

    resultado = gerenciador.listar_por_status(
        Projeto.STATUS_ATIVO
    )

    assert resultado == [projeto1]


def test_listar_projetos_arquivados(gerenciador):
    projeto1 = gerenciador.criar_projeto("Livro 1", "livro")
    projeto2 = gerenciador.criar_projeto("Livro 2", "livro")

    gerenciador.arquivar_projeto(projeto1.id)

    resultado = gerenciador.listar_por_status(
        Projeto.STATUS_ARQUIVADO
    )

    assert resultado == [projeto1]


def test_listar_status_sem_resultados(gerenciador):
    gerenciador.criar_projeto("Livro ativo", "livro")

    resultado = gerenciador.listar_por_status(
        Projeto.STATUS_ARQUIVADO
    )

    assert resultado == []


def test_listar_status_invalido(gerenciador):
    import pytest

    with pytest.raises(ValueError):
        gerenciador.listar_por_status("excluido")

def test_criar_projeto_cria_estrutura_de_diretorios(gerenciador):
    projeto = gerenciador.criar_projeto("Meu Livro", "livro")

    diretorio = (
        gerenciador.gerenciador_diretorios.diretorio_base
        / str(projeto.id)
    )

    assert (diretorio / "arquivos").is_dir()
    assert (diretorio / "materiais").is_dir()
    assert (diretorio / "resultados").is_dir()


def test_falha_ao_salvar_remove_estrutura_e_nao_adiciona_projeto(
    gerenciador,
    monkeypatch,
):
    def falhar_salvamento(projetos):
        raise OSError("Falha simulada na gravação.")

    monkeypatch.setattr(
        gerenciador.armazenamento,
        "salvar",
        falhar_salvamento,
    )

    with pytest.raises(OSError):
        gerenciador.criar_projeto("Projeto de teste", "livro")

    diretorio_base = (
        gerenciador.gerenciador_diretorios.diretorio_base
    )

    assert gerenciador.projetos == []
    assert list(diretorio_base.iterdir()) == []