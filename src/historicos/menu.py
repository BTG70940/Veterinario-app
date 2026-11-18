from .historicoMedicamentos import mostrar_medicamentos

def menu_historicos(USER_LOGADO):
    while True:
        print("\n=== Menu de Historicos ===")
        print("1. Medicamentos")
        print("0. Voltar")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":

            # aqui deve ser colocao o id do animal do dono logado
            # por enquanto vai usar o id 1 sempre

            mostrar_medicamentos(USER_LOGADO)

        elif escolha == "0":
            print("A voltar...")
            break
        else:
            print("Opção inválida. Tenta novamente.")
