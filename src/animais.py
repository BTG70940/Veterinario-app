import json
import os
import sqlite3
from datetime import date, datetime

BASE_DADOS = "veterinario.db"
FICHEIRO_JSON = "animais.json"  # usado apenas para importar dados antigos


# ---------- Base de dados ----------

def ligar():
    conn = sqlite3.connect(BASE_DADOS)
    conn.row_factory = sqlite3.Row  # permite aceder às colunas por nome
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def criar_tabelas(conn):
    with conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS donos (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                nome      TEXT NOT NULL,
                contacto  TEXT NOT NULL,
                UNIQUE (nome, contacto)
            );

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
        """)


def obter_ou_criar_dono(conn, nome, contacto):
    """Reutiliza o dono se já existir (mesmo nome e contacto), senão cria."""
    linha = conn.execute(
        "SELECT id FROM donos WHERE nome = ? AND contacto = ?", (nome, contacto)
    ).fetchone()
    if linha:
        return linha["id"]
    cur = conn.execute(
        "INSERT INTO donos (nome, contacto) VALUES (?, ?)", (nome, contacto)
    )
    return cur.lastrowid


def importar_json(conn):
    """Se existir um animais.json antigo e a base de dados estiver vazia,
    oferece-se para importar os registos."""
    if not os.path.exists(FICHEIRO_JSON):
        return
    if conn.execute("SELECT COUNT(*) FROM animais").fetchone()[0] > 0:
        return
    resposta = input(f"Encontrei {FICHEIRO_JSON}. Importar para a base de dados? (s/n): ")
    if resposta.strip().lower() != "s":
        return
    with open(FICHEIRO_JSON, "r", encoding="utf-8") as f:
        dados = json.load(f)
    with conn:
        for a in dados:
            dono_id = obter_ou_criar_dono(conn, a["dono"]["nome"], a["dono"]["contacto"])
            conn.execute(
                """INSERT INTO animais
                   (id, nome, especie, raca, data_nascimento, sexo, peso_kg,
                    dono_id, notas, data_inscricao)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (a["id"], a["nome"], a["especie"], a["raca"] or None,
                 a["data_nascimento"] or None, a["sexo"] or None, a["peso_kg"],
                 dono_id, a["notas"] or None, a["data_inscricao"]),
            )
    print(f"{len(dados)} animais importados.")


# ---------- Entrada de dados ----------

def pedir_texto(mensagem, obrigatorio=True):
    while True:
        valor = input(mensagem).strip()
        if valor or not obrigatorio:
            return valor
        print("Este campo é obrigatório.")


def pedir_data(mensagem):
    """Pede DD-MM-AAAA e devolve AAAA-MM-DD (ou None se vazio)."""
    while True:
        valor = input(mensagem).strip()
        if not valor:
            return None
        try:
            return datetime.strptime(valor, "%d-%m-%Y").date().isoformat()
        except ValueError:
            print("Data inválida. Usa o formato DD-MM-AAAA (ou deixa vazio).")


def pedir_peso(mensagem):
    while True:
        valor = input(mensagem).strip().replace(",", ".")
        if not valor:
            return None
        try:
            peso = float(valor)
            if peso > 0:
                return peso
        except ValueError:
            pass
        print("Peso inválido. Escreve um número positivo (ou deixa vazio).")


# ---------- Funcionalidades ----------

def registar_animal(conn):
    print("\n--- Novo animal ---")
    nome = pedir_texto("Nome: ")
    especie = pedir_texto("Espécie (cão, gato...): ")
    raca = pedir_texto("Raça: ", obrigatorio=False) or None
    nascimento = pedir_data("Data de nascimento (DD-MM-AAAA): ")
    sexo = pedir_texto("Sexo (M/F): ", obrigatorio=False).upper() or None
    peso = pedir_peso("Peso em kg: ")
    dono_nome = pedir_texto("Nome do dono: ")
    dono_contacto = pedir_texto("Contacto do dono: ")
    notas = pedir_texto("Notas clínicas: ", obrigatorio=False) or None

    with conn:  # se algo falhar, nada fica gravado a meio
        dono_id = obter_ou_criar_dono(conn, dono_nome, dono_contacto)
        cur = conn.execute(
            """INSERT INTO animais
               (nome, especie, raca, data_nascimento, sexo, peso_kg,
                dono_id, notas, data_inscricao)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (nome, especie, raca, nascimento, sexo, peso,
             dono_id, notas, date.today().isoformat()),
        )
    print(f"\nAnimal registado com o ID {cur.lastrowid}.")


def mostrar_animal(a):
    peso = f"{a['peso_kg']} kg" if a["peso_kg"] else "—"
    print(f"\nID: {a['id']}")
    print(f"Nome: {a['nome']}")
    print(f"Espécie: {a['especie']}   Raça: {a['raca'] or '—'}")
    print(f"Nascimento: {a['data_nascimento'] or '—'}   Sexo: {a['sexo'] or '—'}   Peso: {peso}")
    print(f"Dono: {a['dono_nome']} ({a['dono_contacto']})")
    print(f"Notas: {a['notas'] or '—'}")
    print(f"Inscrito em: {a['data_inscricao']}")


CONSULTA_FICHA = """
    SELECT a.*, d.nome AS dono_nome, d.contacto AS dono_contacto
    FROM animais a
    JOIN donos d ON d.id = a.dono_id
"""


def listar_animais(conn):
    print("\n--- Todos os animais ---")
    linhas = conn.execute(CONSULTA_FICHA + " ORDER BY a.id").fetchall()
    if not linhas:
        print("Ainda não há animais registados.")
        return
    for a in linhas:
        print(f"[{a['id']}] {a['nome']} - {a['especie']} - dono: {a['dono_nome']}")


def pesquisar_animais(conn):
    termo = pedir_texto("Pesquisar por nome do animal ou do dono: ")
    padrao = f"%{termo}%"
    linhas = conn.execute(
        CONSULTA_FICHA + " WHERE a.nome LIKE ? OR d.nome LIKE ? ORDER BY a.nome",
        (padrao, padrao),
    ).fetchall()
    if not linhas:
        print("Nenhum resultado.")
        return
    for a in linhas:
        mostrar_animal(a)


def ver_ficha(conn):
    try:
        id_animal = int(input("ID do animal: "))
    except ValueError:
        print("ID inválido.")
        return
    a = conn.execute(CONSULTA_FICHA + " WHERE a.id = ?", (id_animal,)).fetchone()
    if a:
        mostrar_animal(a)
    else:
        print("Animal não encontrado.")


