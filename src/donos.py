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
    return id_dono


def listar_donos():
    """Mostra todos os donos registados."""
    donos = db.consultar(
        "SELECT id, nome, contacto, email FROM donos ORDER BY nome")
    if not donos:
        print("Ainda não há donos registados.")
        return
    for dono in donos:
        print(
            f"[{dono['id']}] {dono['nome']} | {dono['contacto']} | {dono['email'] or '—'}")


def menu_donos():
    """Submenu de gestão de donos."""
    while True:
        print("\n--- Donos ---")
        print("1. Registar dono")
        print("2. Listar donos")
        print("3. Atualizar dono")
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


def atualizar_dono():
    """Altera os dados de um dono existente."""
    listar_donos()
    id_dono = input("Id do dono a atualizar: ").strip()
    if not id_dono.isdigit():
        print("Id inválido.")
        return

    linhas = db.consultar("SELECT * FROM donos WHERE id = ?", (int(id_dono),))
    if not linhas:
        print("Dono não encontrado.")
        return

    dono = linhas[0]
    print("Deixa em branco para manter o valor atual.")
    nome = input(f"Nome [{dono['nome']}]: ").strip() or dono["nome"]
    contacto = input(
        f"Contacto [{dono['contacto']}]: ").strip() or dono["contacto"]
    email = input(f"Email [{dono['email'] or '—'}]: ").strip() or dono["email"]
    morada = input(
        f"Morada [{dono['morada'] or '—'}]: ").strip() or dono["morada"]

    try:
        db.executar(
            "UPDATE donos SET nome = ?, contacto = ?, email = ?, morada = ? WHERE id = ?",
            (nome, contacto, email, morada, int(id_dono)),
        )
    except sqlite3.IntegrityError:
        print("Já existe outro dono com esse nome e contacto.")
        return
    print("Dono atualizado.")
