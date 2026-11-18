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

    ligacao = ligar()
    try:
        ligacao.execute(
            """
            CREATE TABLE IF NOT EXISTS animais (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                nome             TEXT NOT NULL,
                especie          TEXT NOT NULL,
                raca             TEXT,
                data_nascimento  TEXT,
                sexo             TEXT,
                peso_kg          REAL CHECK (peso_kg IS NULL OR peso_kg > 0),
                dono_id          INTEGER NOT NULL REFERENCES donos(id),
                notas            TEXT,
                data_inscricao   TEXT NOT NULL
            );
            """
        )
        ligacao.commit()
    finally:
        ligacao.close()

    ligacao = ligar()
    try:
        ligacao.execute(
            """
            CREATE TABLE IF NOT EXISTS medicamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_medicamento TEXT NOT NULL,
                quantidade INTEGER,
                id_animal INETEGER
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

def utilizador_existe(nome):
    conn = ligar()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM donos WHERE nome = ? LIMIT 1",
            (nome,),
        )
        return cursor.fetchone() is not None
    finally:
        conn.close()

def obter_id_dono(nome):
    conn = sqlite3.connect(CAMINHO_BD)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM donos WHERE nome = ? LIMIT 1",
            (nome,),
        )
        linha = cursor.fetchone()
        return linha[0] if linha else None
    finally:
        conn.close()


def obter_id_animais_por_dono(dono):
    conn = sqlite3.connect(CAMINHO_BD)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM animais WHERE dono_id = ?",
            (dono,)
        )
        linha = cursor.fetchall()

        return [row[0] for row in linha] if linha else []
        
    finally:
        conn.close()

def obter_medicamentos_por_animal(animal_id):
    """
    Devolve uma lista única com todos os medicamentos
    associados aos animais indicados.

    Parâmetros:
        caminho_bd (str): caminho para a base de dados SQLite.
        animal_id (list): lista com os IDs dos animais.

    Retorna:
        list[dict]: lista de medicamentos com os campos
                    id, nome_medicamento, quantidade e id_animal.
    """

    if not animal_id:
        return []

    if isinstance(animal_id, int):
        animal_id = [animal_id]

    # Remove IDs None da lista
    animal_id = [id for id in animal_id if id is not None]

    if not animal_id:
        return []

    conn = sqlite3.connect(CAMINHO_BD)

    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in animal_id)

        cursor.execute(
            f"""
            SELECT id, nome_medicamento, quantidade, id_animal
            FROM medicamentos
            WHERE id_animal IN ({placeholders})
            """,
            tuple(animal_id)
        )

        return [dict(linha) for linha in cursor.fetchall()]

    finally:
        conn.close()
