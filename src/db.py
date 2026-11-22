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

        ligacao = ligar()
    try:
        ligacao.execute(
            """
            CREATE TABLE IF NOT EXISTS doencas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                consulta_id INTEGER NOT NULL REFERENCES consultas(id)
            );
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
    """
    Verifica se existe um dono com o nome indicado na base de dados.

    Executa uma consulta à tabela ``donos`` para verificar se existe
    algum registo cujo nome corresponda ao valor fornecido.

    :param nome: Nome do dono que se pretende procurar.
    :type nome: str
    :return: True se existir um dono com o nome indicado,
             ou False caso contrário.
    :rtype: bool
    :raises sqlite3.Error: Se ocorrer um erro durante a consulta à base de dados.
    """
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
    """
    Obtém o identificador de um dono através do seu nome.

    Executa uma consulta à base de dados para procurar o dono
    com o nome indicado. Caso exista, devolve o seu identificador.
    Se não encontrar nenhum registo correspondente, devolve None.

    :param nome: Nome do dono que se pretende procurar.
    :type nome: str
    :return: Identificador do dono, caso exista, ou None se não for encontrado.
    :rtype: int | None
    :raises sqlite3.Error: Se ocorrer um erro durante a consulta à base de dados.
    """
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
    """
    Obtém a lista de identificadores dos animais pertencentes a um determinado dono.

    Executa uma consulta à base de dados para obter os IDs dos animais
    associados ao dono indicado.

    :param dono: Identificador do dono cujos animais se pretende consultar.
    :type dono: int
    :return: Lista de identificadores dos animais pertencentes ao dono.
             Caso não existam animais associados, devolve uma lista vazia.
    :rtype: list[int]
    :raises sqlite3.Error: Se ocorrer um erro durante a consulta à base de dados.
    """
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
            SELECT
                m.id,
                m.nome_medicamento,
                m.quantidade,
                m.id_animal,
                a.nome AS nome_animal
            FROM medicamentos m
            INNER JOIN animais a ON m.id_animal = a.id
            WHERE m.id_animal IN ({placeholders})
            ORDER BY a.nome, m.nome_medicamento
            """,
            tuple(animal_id)
        )

        return [dict(linha) for linha in cursor.fetchall()]

    finally:
        conn.close()


def obter_animais_a_tomar_medicacao(dono_id):
    """
    Devolve uma lista de animais do dono indicado que têm medicação registada.

    Parâmetros:
        dono_id (int): ID do dono.

    Retorna:
        list[dict]: lista de animais com os campos
                    id, nome, especie, raca, nome_medicamento e quantidade.
    """

    conn = sqlite3.connect(CAMINHO_BD)

    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT a.id, a.nome, a.especie, a.raca,
                   m.nome_medicamento, m.quantidade
            FROM animais a
            JOIN medicamentos m ON a.id = m.id_animal
            WHERE a.dono_id = ?
            """,
            (dono_id,)
        )

        return [dict(linha) for linha in cursor.fetchall()]

    finally:
        conn.close()

def obter_doencas_por_animal(animal_id):
    """
    Devolve todas as doenças associadas aos animais indicados.

    Retorna:
        list[dict]: lista de doenças com os campos
                    id, nome, descricao, consulta_id,
                    id_animal, nome_animal e data.
    """

    if not animal_id:
        return []

    if isinstance(animal_id, int):
        animal_id = [animal_id]

    animal_id = list(dict.fromkeys(
        id for id in animal_id if id is not None
    ))

    if not animal_id:
        return []

    conn = sqlite3.connect(CAMINHO_BD)

    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in animal_id)

        cursor.execute(
            f"""
            SELECT
                d.id,
                d.nome,
                d.descricao,
                d.consulta_id,
                c.animal_id AS id_animal,
                a.nome AS nome_animal,
                c.data
            FROM doencas d
            JOIN consultas c ON d.consulta_id = c.id
            JOIN animais a ON c.animal_id = a.id
            WHERE c.animal_id IN ({placeholders})
            ORDER BY a.nome, c.data DESC
            """,
            tuple(animal_id)
        )

        return [dict(linha) for linha in cursor.fetchall()]

    finally:
        conn.close()


FUNCAO_MEDICO = "Médico veterinário"

def criar_tabela_colaboradores():
    """Cria a tabela dos médicos e outros colaboradores da clínica, caso não exista."""
    executar(
        """
        CREATE TABLE IF NOT EXISTS colaboradores (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            nome          TEXT NOT NULL,
            funcao        TEXT NOT NULL,
            especialidade TEXT,
            contacto      TEXT,
            email         TEXT
        )
        """
    )        


# ---------- Marcação de consultas (story 9) ----------

def criar_tabela_marcacoes():
    """
    Cria a tabela das consultas marcadas pelos donos, caso não exista.
    Se o médico for eliminado, a marcação fica sem médico (ON DELETE SET NULL).
    """
    executar(
        """
        CREATE TABLE IF NOT EXISTS marcacoes (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            animal_id      INTEGER NOT NULL REFERENCES animais(id),
            data_hora      TEXT NOT NULL,
            motivo         TEXT NOT NULL,
            colaborador_id INTEGER REFERENCES colaboradores(id) ON DELETE SET NULL,
            estado         TEXT NOT NULL DEFAULT 'marcada'
                           CHECK (estado IN ('marcada', 'cancelada'))
        )
        """
    )


# ---------- Eliminação de dados (stories 16 e 17) ----------

def tabela_existe(ligacao, nome):
    """Devolve True se a tabela indicada existir na base de dados."""
    return ligacao.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = ?", (nome,)
    ).fetchone() is not None


def apagar_dados_animais(ligacao, ids_animais):
    """
    Apaga os animais indicados e tudo o que depende deles
    (doenças, consultas, vacinas, medicamentos e marcações).

    Não faz commit: deve ser chamada dentro de um `with ligacao:`,
    para que ou se apaga tudo, ou não se apaga nada.

    Parâmetros:
        ligacao (sqlite3.Connection): ligação aberta à base de dados.
        ids_animais (list[int]): IDs dos animais a apagar.
    """
    ids = list(ids_animais)
    if not ids:
        return
    marcadores = ",".join("?" for _ in ids)

    if tabela_existe(ligacao, "doencas") and tabela_existe(ligacao, "consultas"):
        ligacao.execute(
            f"DELETE FROM doencas WHERE consulta_id IN "
            f"(SELECT id FROM consultas WHERE animal_id IN ({marcadores}))",
            ids,
        )
    for tabela, coluna in (
        ("consultas", "animal_id"),
        ("vacinas", "animal_id"),
        ("marcacoes", "animal_id"),
        ("medicamentos", "id_animal"),
        ("animais", "id"),
    ):
        if tabela_existe(ligacao, tabela):
            ligacao.execute(
                f"DELETE FROM {tabela} WHERE {coluna} IN ({marcadores})", ids)


def eliminar_dono(dono_id):
    """
    Apaga o dono, os seus animais e todos os dados associados (story 16).
    É tudo feito numa só transação: ou apaga tudo, ou não apaga nada.
    """
    ligacao = ligar()
    try:
        with ligacao:
            ids = [linha["id"] for linha in ligacao.execute(
                "SELECT id FROM animais WHERE dono_id = ?", (dono_id,))]
            apagar_dados_animais(ligacao, ids)
            ligacao.execute("DELETE FROM donos WHERE id = ?", (dono_id,))
    finally:
        ligacao.close()