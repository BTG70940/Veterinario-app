"""Área de administração da clínica."""
import db


def contar_animais():
    """Mostra quantos animais estão registados na clínica."""
    linhas = db.consultar("SELECT COUNT(*) AS total FROM animais")
    total = linhas[0]["total"]
    if total == 1:
        print("Há 1 animal registado.")
    else:
        print(f"Há {total} animais registados.")


def menu_administracao():
    """Submenu da área de administração."""
    while True:
        print("\n--- Administração ---")
        print("1. Quantos animais estão registados")
        print("0. Voltar")
        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            contar_animais()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")
