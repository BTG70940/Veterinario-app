"""Área de administração da clínica: animais, donos, fornecedores e produtos."""
import sqlite3

import animais
import db
import donos


def criar_tabelas_admin():
    """Cria as tabelas de fornecedores e produtos, caso ainda não existam."""
    db.executar(
        """
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            contacto TEXT,
            email TEXT,
            morada TEXT
        )
        """
    )
    db.executar(
        """
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT,
            preco REAL NOT NULL CHECK (preco >= 0),
            stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
            fornecedor_id INTEGER REFERENCES fornecedores(id)
        )
        """
    )


def _pedir_id(mensagem):
    """Pede um id e devolve-o como inteiro (ou None se não for um número)."""
    valor = input(mensagem).strip()
    return int(valor) if valor.isdigit() else None


def _pedir_numero(mensagem, tipo, atual=None):
    """Pede um número >= 0. Se atual for dado, vazio mantém o valor atual."""
    while True:
        valor = input(mensagem).strip().replace(",", ".")
        if not valor and atual is not None:
            return atual
        try:
            numero = tipo(valor)
            if numero >= 0:
                return numero
        except ValueError:
            pass
        print("Valor inválido. Escreve um número igual ou superior a 0.")


def contar_animais():
    """Mostra quantos animais estão registados na clínica."""
    total = db.consultar("SELECT COUNT(*) AS total FROM animais")[0]["total"]
    if total == 1:
        print("Há 1 animal registado.")
    else:
        print(f"Há {total} animais registados.")


def listar_todos_animais():
    """Lista todos os animais registados."""
    conn = animais.ligar()
    try:
        animais.listar_animais(conn)
    finally:
        conn.close()


def pesquisar_todos_animais():
    """Pesquisa animais pelo nome do animal ou do dono."""
    conn = animais.ligar()
    try:
        animais.pesquisar_animais(conn)
    finally:
        conn.close()
