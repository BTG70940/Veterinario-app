from .historicoMedicamentos import mostrar_medicamentos

def menu_historicos(USER_LOGADO):
    while True:
        print("\n=== Menu de Historicos ===")
        print("1. Medicamentos")
        print("0. Voltar")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            mostrar_medicamentos(USER_LOGADO)

        elif escolha == "0":
            print("A voltar...")
            break
        else:
            print("Opção inválida. Tenta novamente.")
