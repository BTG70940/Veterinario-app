"""Área de administração da clínica."""
import db
import getpass
import hashlib
import hmac


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


# ---------- Acesso restrito ----------

# Hash SHA-256 da palavra-passe de administrador (a palavra-passe em si não é guardada).
HASH_ADMIN = "COLA_AQUI_O_HASH"


def verificar_admin():
    """Pede a palavra-passe de administrador. Devolve True se estiver correta."""
    for _ in range(3):
        tentativa = getpass.getpass("Palavra-passe de administrador: ")
        hash_tentativa = hashlib.sha256(tentativa.encode()).hexdigest()
        if hmac.compare_digest(hash_tentativa, HASH_ADMIN):
            return True
        print("Palavra-passe incorreta.")
    print("Demasiadas tentativas. Acesso negado.")
    return False
