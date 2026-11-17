def menu_medicamentos():
    while True:
        print("\n=== Menu de Historicos ===")
        print("1. Medicamentos")
        print("0. Voltar")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            print("\nAbrir secção de medicamentos...")
            # Aqui podes chamar a tua função/lógica de medicamentos
        elif escolha == "0":
            print("A voltar...")
            break
        else:
            print("Opção inválida. Tenta novamente.")
