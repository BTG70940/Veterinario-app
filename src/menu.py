"""Menu principal da aplicação."""
import donos
import animais
import administracao
import marcacoes
from db import obter_animais_a_tomar_medicacao
from historicos import menu


def mostrar_animais_com_medicacao(user_logado):
    """
    Mostra os animais diferentes que têm medicação registada.

    Parâmetros:
        user_logado (int): ID do dono autenticado.
    """

    animais = obter_animais_a_tomar_medicacao(user_logado)

    if not animais:
        return

    print("\n===== ATENÇÃO: SEUS ANIMAIS A TOMAR MEDICAÇÃO =====")

    animais_unicos = {}

    for animal in animais:
        animais_unicos[animal["id"]] = animal

    for animal in animais_unicos.values():
        print(
            f"- {animal['nome']} "
            f"({animal['especie']})"
        )

    print("=======================================================")




def menu_principal(USER_LOGADO):
    """Mostra o menu principal e encaminha para cada área."""
    while True:
        mostrar_animais_com_medicacao(USER_LOGADO)
        print("\n=== Clínica Veterinária ===")
        print("1. Donos")
        print("2. Animais")
        print("3. Consultas")
        print("4. Históricos")
        print("5. Administração")
        print("6. Eliminar a minha conta")
        print("0. Sair")
        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            donos.menu_donos()  # story 2
        elif opcao == "2":
            animais.menu(USER_LOGADO)  # stories 3, 5, 6, 17  
        elif opcao == "3":
            marcacoes.menu_marcacoes(USER_LOGADO)  # story 9
        elif opcao == "4":
            menu.menu_historicos(USER_LOGADO)  # stories 10, 11
        elif opcao == "5":
            administracao.menu_administracao()  # stories 8, 14
        elif opcao == "6":
            if donos.eliminar_conta(USER_LOGADO):  # story 16
                print("Sessão terminada.")
                break
        elif opcao == "0":
            print("Até breve!")
            break
        else:
            print("Opção inválida, tenta outra vez.")
