"""Ponto de entrada da aplicação."""
import db
from menu import menu_principal
from donos import adicionar_dono

User_logado = 0

def menu_autenticacao():
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
                User_logado = db.obter_id_dono(nome)
                break
            else:
                print("User nao existe")    
        elif escolha == "2":
            User_logado = adicionar_dono()
            break
        elif escolha == "0":
            break
        else:
            print("Opção inválida. Tenta novamente.")



def main():
    db.criar_tabelas()
    menu_autenticacao()
    menu_principal()


if __name__ == "__main__":
    main()
