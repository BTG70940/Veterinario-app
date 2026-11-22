from .historicos import mostrar_medicamentos, mostrar_historico_doencas

def menu_historicos(USER_LOGADO):
    """
    Apresenta o menu de consulta dos históricos do utilizador
    e encaminha para a área selecionada.

    Permite ao utilizador consultar o histórico de medicamentos
    ou o histórico de doenças. O menu permanece em execução até
    o utilizador selecionar a opção de voltar.

    :param USER_LOGADO: Identificador do utilizador atualmente autenticado.
    :type USER_LOGADO: int
    :return: Não devolve nenhum valor. Apresenta o menu e executa
             a funcionalidade correspondente à opção selecionada.
    :rtype: None
    """
    while True:
        print("\n=== Menu de Historicos ===")
        print("1. Medicamentos")
        print("2. Doenças")
        print("0. Voltar")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            mostrar_medicamentos(USER_LOGADO)

        if escolha == "2":
            mostrar_historico_doencas(USER_LOGADO)

        elif escolha == "0":
            print("A voltar...")
            break
        else:
            print("Opção inválida. Tenta novamente.")
