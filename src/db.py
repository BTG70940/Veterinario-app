"""Ligação à base de dados SQLite da aplicação."""
import sqlite3
from pathlib import Path

CAMINHO_BD = Path(__file__).resolve().parent.parent / "veterinario.db"


def ligar():
    """Abre uma ligação à base de dados e devolve-a."""
    ligacao = sqlite3.connect(CAMINHO_BD)
    ligacao.row_factory = sqlite3.Row
    ligacao.execute("PRAGMA foreign_keys = ON")
    return ligacao


def criar_tabelas():
    """Cria as tabelas da aplicação, caso ainda não existam."""
    ligacao = ligar()
    try:
        ligacao.execute(
            """
            CREATE TABLE IF NOT EXISTS donos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                contacto TEXT NOT NULL,
                email TEXT,
                morada TEXT,
                UNIQUE (nome, contacto)
            )
            """
        )
        ligacao.commit()
    finally:
        ligacao.close()


def executar(sql, parametros=()):
    """Executa INSERT, UPDATE ou DELETE. Devolve o id da última linha inserida."""
    ligacao = ligar()
    try:
        cursor = ligacao.execute(sql, parametros)
        ligacao.commit()
        return cursor.lastrowid
    finally:
        ligacao.close()


def consultar(sql, parametros=()):
    """Executa um SELECT e devolve todas as linhas."""
    ligacao = ligar()
    try:
        return ligacao.execute(sql, parametros).fetchall()
    finally:
        ligacao.close()
