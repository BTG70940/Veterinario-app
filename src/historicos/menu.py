from .historicos import mostrar_medicamentos, mostrar_historico_doencas

def menu_historicos(USER_LOGADO):
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
