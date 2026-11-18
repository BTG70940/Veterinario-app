"""Ponto de entrada da aplicação."""
import db
from menu import menu_principal
from donos import adicionar_dono

USER_LOGADO = 0

def menu_autenticacao():
    global USER_LOGADO
    while True:
        print("\n=== Autenticação ===")
        print("1. Login")
        print("2. Registar")
        print("0. Sair")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            nome = input("Nome: ").strip()

            if not nome:
                print("O nome não pode estar vazio.")
                continue

            if db.utilizador_existe(nome):
                print(f"Login efetuado. Bem-vindo, {nome}!")
                USER_LOGADO = db.obter_id_dono(nome)
                break
            else:
                print("User nao existe")    
        elif escolha == "2":
            USER_LOGADO = adicionar_dono()
            break
        elif escolha == "0":
            exit()
        else:
            print("Opção inválida. Tenta novamente.")



def main():
    db.criar_tabelas()
    menu_autenticacao()
    menu_principal(USER_LOGADO)


if __name__ == "__main__":
    main()
