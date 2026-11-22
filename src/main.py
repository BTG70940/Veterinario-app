"""Ponto de entrada da aplicação."""
import db
from menu import menu_principal
from donos import adicionar_dono

USER_LOGADO = 0

def menu_autenticacao():
    """
    Apresenta o menu de autenticação e permite ao utilizador iniciar sessão,
    registar-se na aplicação ou sair do programa.

    Disponibiliza três opções:

    - Login: solicita o nome do utilizador e verifica se este existe
      na base de dados. Caso exista, obtém o respetivo identificador
      e inicia a sessão.
    - Registar: permite adicionar um novo dono através da função
      ``adicionar_dono()``.
    - Sair: termina a execução do programa.

    O identificador do utilizador autenticado é guardado na variável
    global ``USER_LOGADO``. O menu permanece em execução até que
    o utilizador consiga iniciar sessão, se registe ou saia da aplicação.

    :return: Não devolve nenhum valor. Atualiza a variável global
             ``USER_LOGADO`` com o identificador do utilizador autenticado.
    :rtype: None
    """
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
    """Cria as tabelas, faz o login ou registo e abre o menu principal."""
    db.criar_tabelas()
    db.criar_tabela_colaboradores()
    db.criar_tabela_marcacoes()
    menu_autenticacao()
    menu_principal(USER_LOGADO)


if __name__ == "__main__":
    main()
