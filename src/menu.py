"""Menu principal da aplicação."""
import donos

def menu_principal():
    """Mostra o menu principal e encaminha para cada área."""
    while True:
        print("\n=== Clínica Veterinária ===")
        print("1. Donos")
        print("2. Animais")
        print("3. Consultas")
        print("4. Históricos")
        print("5. Administração")
        print("0. Sair")
        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            donos.menu_donos() # story 2
        elif opcao == "2":
            print("Em construção...")  # stories 3, 5, 6
        elif opcao == "3":
            print("Em construção...")  # story 9
        elif opcao == "4":
            print("Em construção...")  # stories 10, 11
        elif opcao == "5":
            print("Em construção...")  # stories 8, 14
        elif opcao == "0":
            print("Até breve!")
            break
        else:
            print("Opção inválida, tenta outra vez.")
