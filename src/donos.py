"""Gestão dos donos dos animais."""
import sqlite3

import db


def adicionar_dono():
    """Pede os dados ao utilizador e guarda um novo dono."""
    nome = input("Nome: ").strip()
    contacto = input("Contacto: ").strip()
    if not nome or not contacto:
        print("O nome e o contacto são obrigatórios.")
        return
    email = input("Email (opcional): ").strip() or None
    morada = input("Morada (opcional): ").strip() or None

    try:
        id_dono = db.executar(
            "INSERT INTO donos (nome, contacto, email, morada) VALUES (?, ?, ?, ?)",
            (nome, contacto, email, morada),
        )
    except sqlite3.IntegrityError:
        print("Já existe um dono com esse nome e contacto.")
        return
    print(f"Dono registado com o id {id_dono}.")


def listar_donos():
    """Mostra todos os donos registados."""
    donos = db.consultar("SELECT id, nome, contacto, email FROM donos ORDER BY nome")
    if not donos:
        print("Ainda não há donos registados.")
        return
    for dono in donos:
        print(f"[{dono['id']}] {dono['nome']} | {dono['contacto']} | {dono['email'] or '—'}")


def menu_donos():
    """Submenu de gestão de donos."""
    while True:
        print("\n--- Donos ---")
        print("1. Registar dono")
        print("2. Listar donos")
        print("0. Voltar")
        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            adicionar_dono()
        elif opcao == "2":
            listar_donos()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")
