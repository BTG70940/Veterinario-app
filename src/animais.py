
import json
import os
import sqlite3
from datetime import date, datetime
 
BASE_DADOS = "veterinario.db"
FICHEIRO_JSON = "animais.json"  # usado apenas para importar dados antigos
 
 
# ---------- Base de dados ----------
 
def ligar():
    """Abre uma ligação à base de dados SQLite.
    
    Configura o acesso às colunas por nome e ativa a verificação de chaves
    estrangeiras.
    
    Returns:
        sqlite3.Connection: Ligação aberta à base de dados definida em
            ``BASE_DADOS``.
    """
    conn = sqlite3.connect(BASE_DADOS)
    conn.row_factory = sqlite3.Row  # permite aceder às colunas por nome
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
 
 
def criar_tabelas(conn):
    """Cria as tabelas da aplicação caso ainda não existam.
    
    Cria as tabelas ``donos``, ``animais`` e ``consultas``, incluindo as
    chaves estrangeiras e as restrições definidas no esquema.
    
    Args:
        conn (sqlite3.Connection): Ligação à base de dados onde as tabelas
            serão criadas.
    
    Returns:
        None
    """
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
 
            CREATE TABLE IF NOT EXISTS consultas (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id    INTEGER NOT NULL REFERENCES animais(id),
                data         TEXT NOT NULL,
                motivo       TEXT NOT NULL,
                diagnostico  TEXT,
                tratamento   TEXT,
                peso_kg      REAL CHECK (peso_kg IS NULL OR peso_kg > 0)
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
    """Pede um peso positivo em quilogramas.
    
    Aceita vírgula ou ponto como separador decimal. Repete a pergunta se
    o valor não for numérico ou não for positivo; uma resposta vazia é
    aceite.
    
    Args:
        mensagem (str): Texto apresentado ao utilizador.
    
    Returns:
        float | None: Peso introduzido ou ``None`` se o campo ficar vazio.
    """
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
 
 
# ---------- Utilitários ----------
 
def formatar_data(iso):
    """AAAA-MM-DD -> DD-MM-AAAA, para mostrar ao utilizador."""
    if not iso:
        return "—"
    return date.fromisoformat(iso).strftime("%d-%m-%Y")
 
 
def calcular_idade(data_nascimento):
    if not data_nascimento:
        return "—"
    nasc = date.fromisoformat(data_nascimento)
    hoje = date.today()
    meses = (hoje.year - nasc.year) * 12 + hoje.month - nasc.month
    if hoje.day < nasc.day:
        meses -= 1
    anos, meses = divmod(max(meses, 0), 12)
    partes = []
    if anos:
        partes.append(f"{anos} ano" + ("s" if anos != 1 else ""))
    if meses or not anos:
        partes.append(f"{meses} " + ("meses" if meses != 1 else "mês"))
    return " e ".join(partes)
 
 
CONSULTA_FICHA = """
    SELECT a.*, d.nome AS dono_nome, d.contacto AS dono_contacto
    FROM animais a
    JOIN donos d ON d.id = a.dono_id
"""
 
 
def escolher_animal(conn):
    """Pede um ID, nome do animal ou nome do dono e devolve o animal escolhido."""
    termo = pedir_texto("ID, nome do animal ou nome do dono: ")
    if termo.isdigit():
        linhas = conn.execute(CONSULTA_FICHA + " WHERE a.id = ?", (int(termo),)).fetchall()
    else:
        padrao = f"%{termo}%"
        linhas = conn.execute(
            CONSULTA_FICHA + " WHERE a.nome LIKE ? OR d.nome LIKE ? ORDER BY a.nome",
            (padrao, padrao),
        ).fetchall()
 
    if not linhas:
        print("Animal não encontrado.")
        return None
    if len(linhas) == 1:
        return linhas[0]
 
    print("\nVárias correspondências:")
    for a in linhas:
        print(f"  [{a['id']}] {a['nome']} - {a['especie']} - dono: {a['dono_nome']}")
    try:
        escolhido = int(input("Escolhe o ID: "))
    except ValueError:
        print("ID inválido.")
        return None
    for a in linhas:
        if a["id"] == escolhido:
            return a
    print("ID não está na lista.")
    return None
 
 
# ---------- Funcionalidades ----------
 
def registar_animal(conn):
    """Pede os dados do animal e do dono e guarda o animal"""
    
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
 
 
def listar_animais(conn):
    """Mostra todos os animais registados com o nome do dono."""
    print("\n--- Todos os animais ---")
    linhas = conn.execute(CONSULTA_FICHA + " ORDER BY a.id").fetchall()
    if not linhas:
        print("Ainda não há animais registados.")
        return
    for a in linhas:
        print(f"[{a['id']}] {a['nome']} - {a['especie']} - dono: {a['dono_nome']}")
 
 
def pesquisar_animais(conn):
    """Pesquisa animais pelo nome do animal ou dono"""
    
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
        print(f"[{a['id']}] {a['nome']} - {a['especie']} - dono: {a['dono_nome']}")
 
 
def registar_consulta(conn):
    """Regista uma consulta de um animal e, se existir, a doença identificada."""
    
    print("\n--- Nova consulta ---")
    animal = escolher_animal(conn)
    if not animal:
        return
    print(f"Animal: {animal['nome']} ({animal['especie']})")
    motivo = pedir_texto("Motivo da consulta: ")
    diagnostico = pedir_texto("Diagnóstico: ", obrigatorio=False) or None
    tratamento = pedir_texto("Tratamento: ", obrigatorio=False) or None
    peso = pedir_peso("Peso atual em kg (vazio para não alterar): ")
 
    with conn:
        conn.execute(
            """INSERT INTO consultas
               (animal_id, data, motivo, diagnostico, tratamento, peso_kg)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (animal["id"], date.today().isoformat(), motivo, diagnostico, tratamento, peso),
        )
        if peso:  # mantém o peso atual do animal em dia
            conn.execute("UPDATE animais SET peso_kg = ? WHERE id = ?", (peso, animal["id"]))
    print("Consulta registada.")
 
 
def consultar_situacao(conn):
    """Resumo da situação atual do animal: dados, última consulta e historial."""
    print("\n--- Situação atual do animal ---")
    a = escolher_animal(conn)
    if not a:
        return
 
    consultas = conn.execute(
        "SELECT * FROM consultas WHERE animal_id = ? ORDER BY data DESC, id DESC",
        (a["id"],),
    ).fetchall()
 
    peso = f"{a['peso_kg']} kg" if a["peso_kg"] else "—"
    print(f"\n=== {a['nome']} (ID {a['id']}) ===")
    print(f"Espécie: {a['especie']}   Raça: {a['raca'] or '—'}   Sexo: {a['sexo'] or '—'}")
    print(f"Idade: {calcular_idade(a['data_nascimento'])}   Peso atual: {peso}")
    print(f"Dono: {a['dono_nome']} ({a['dono_contacto']})")
    print(f"Inscrito em: {formatar_data(a['data_inscricao'])}")
    print(f"Notas gerais: {a['notas'] or '—'}")
 
    print("\nÚltima consulta:")
    if not consultas:
        print("  Ainda sem consultas registadas.")
        return
    u = consultas[0]
    print(f"  Data: {formatar_data(u['data'])}")
    print(f"  Motivo: {u['motivo']}")
    print(f"  Diagnóstico: {u['diagnostico'] or '—'}")
    print(f"  Tratamento: {u['tratamento'] or '—'}")
 
    print(f"\nHistorial ({len(consultas)} consulta(s), mais recentes primeiro):")
    for c in consultas[:5]:
        print(f"  {formatar_data(c['data'])} - {c['motivo']}")
    if len(consultas) > 5:
        print(f"  ... e mais {len(consultas) - 5} anterior(es).")
 
 

