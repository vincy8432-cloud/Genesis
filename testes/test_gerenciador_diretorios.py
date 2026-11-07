from src.core.projeto import Projeto
from src.estrutura.gerenciador_diretorios import GerenciadorDiretorios


def test_criar_estrutura_do_projeto(tmp_path):
    gerenciador = GerenciadorDiretorios(
        diretorio_base=tmp_path / "projetos"
    )

    projeto = Projeto("Meu Livro", "livro")

    diretorio = gerenciador.criar_estrutura(projeto)

    assert diretorio.exists()
    assert diretorio == tmp_path / "projetos" / str(projeto.id)

    assert (diretorio / "arquivos").is_dir()
    assert (diretorio / "materiais").is_dir()
    assert (diretorio / "resultados").is_dir()


def test_criar_estrutura_novamente_nao_falha(tmp_path):
    gerenciador = GerenciadorDiretorios(
        diretorio_base=tmp_path / "projetos"
    )

    projeto = Projeto("Meu Livro", "livro")

    primeira_criacao = gerenciador.criar_estrutura(projeto)
    segunda_criacao = gerenciador.criar_estrutura(projeto)

    assert primeira_criacao == segunda_criacao
    assert (segunda_criacao / "arquivos").is_dir()


def test_projetos_tem_diretorios_independentes(tmp_path):
    gerenciador = GerenciadorDiretorios(
        diretorio_base=tmp_path / "projetos"
    )

    projeto1 = Projeto("Livro", "livro")
    projeto2 = Projeto("Música", "musica")

    diretorio1 = gerenciador.criar_estrutura(projeto1)
    diretorio2 = gerenciador.criar_estrutura(projeto2)

    assert diretorio1 != diretorio2
    assert diretorio1.exists()
    assert diretorio2.exists()