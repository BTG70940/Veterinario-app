"""Gestão dos donos dos animais."""
import db


def adicionar_dono():
    """Pede os dados ao utilizador e guarda um novo dono."""
    nome = input("Nome: ").strip()
    if not nome:
        print("O nome é obrigatório.")
        return
    telefone = input("Telefone: ").strip()
    email = input("Email: ").strip()
    morada = input("Morada: ").strip()

    id_dono = db.executar(
        "INSERT INTO donos (nome, telefone, email, morada) VALUES (?, ?, ?, ?)",
        (nome, telefone, email, morada),
    )
    print(f"Dono registado com o id {id_dono}.")


def listar_donos():
    """Mostra todos os donos registados."""
    donos = db.consultar("SELECT id, nome, telefone, email FROM donos ORDER BY nome")
    if not donos:
        print("Ainda não há donos registados.")
        return
    for dono in donos:
        print(f"[{dono['id']}] {dono['nome']} | {dono['telefone']} | {dono['email']}")
