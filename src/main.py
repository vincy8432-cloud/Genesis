from src.core.projeto import Projeto


def main():
    projeto = Projeto(
        "O Último Segundo Antes...",
        "livro"
    )

    print("ID:", projeto.id)
    print("Projeto:", projeto.nome)
    print("Tipo:", projeto.tipo)


if __name__ == "__main__":
    main()