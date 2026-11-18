import json
import os
import re
import sqlite3
import unicodedata
from datetime import date, datetime
from xml.sax.saxutils import escape

from donos import adicionar_dono
 
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
 
            CREATE TABLE IF NOT EXISTS consultas (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id    INTEGER NOT NULL REFERENCES animais(id),
                data         TEXT NOT NULL,
                motivo       TEXT NOT NULL,
                diagnostico  TEXT,
                tratamento   TEXT,
                peso_kg      REAL CHECK (peso_kg IS NULL OR peso_kg > 0)
            );

            CREATE TABLE IF NOT EXISTS vacinas (
                id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                animal_id          INTEGER NOT NULL REFERENCES animais(id),
                nome               TEXT NOT NULL,
                data_administracao TEXT NOT NULL,
                proxima_dose       TEXT,
                lote               TEXT,
                notas              TEXT
            );
            CREATE TABLE IF NOT EXISTS doencas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                consulta_id INTEGER NOT NULL REFERENCES consultas(id)
            );
        """)
 
 

def obter_ou_criar_dono(conn, nome):
    """Reutiliza o dono se existir; caso contrário, cria um novo."""

    linha = conn.execute(
        """
        SELECT id, telefone, morada, contacto
        FROM donos
        WHERE nome = ?
        """,
        (nome,)
    ).fetchall()

    if len(linha) > 1:
        print(f"Encontrados múltiplos donos com o nome '{nome}'.")
        print("Escolhe o ID do dono correto:")

        for l in linha:
            print(
                f"  [{l['id']}] {nome} - "
                f"contacto: {l['contacto']} - "
                f"telefone: {l['telefone']} - "
                f"morada: {l['morada']}"
            )

        while True:
            try:
                escolhido = int(input("ID do dono: "))
            except ValueError:
                print("ID inválido.")
                continue

            for l in linha:
                if l["id"] == escolhido:
                    return l["id"]

            print("ID não está na lista.")

    elif len(linha) == 1:
        return linha[0]["id"]

    else:
        print(f"Não foi encontrado nenhum dono com o nome '{nome}'.")
        print("Vamos registar um novo dono.")

        return adicionar_dono()

 
 
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
            dono_id = obter_ou_criar_dono(conn, a["dono"]["nome"])
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
 
 
def obter_consultas(conn, animal_id):
    """Todas as consultas de um animal, da mais recente para a mais antiga."""
    return conn.execute(
        "SELECT * FROM consultas WHERE animal_id = ? ORDER BY data DESC, id DESC",
        (animal_id,),
    ).fetchall()


def obter_vacinas(conn, animal_id):
    """Todas as vacinas de um animal, da mais recente para a mais antiga."""
    return conn.execute(
        "SELECT * FROM vacinas WHERE animal_id = ? ORDER BY data_administracao DESC, id DESC",
        (animal_id,),
    ).fetchall()
 
 
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
        dono_id = obter_ou_criar_dono(conn, dono_nome)
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
        print(f"[{a['id']}] {a['nome']} - {a['especie']} - dono: {a['dono_nome']}")
 
 

def registar_doenca(conn, consulta_id):
    """Regista uma doença associada a uma consulta."""

    print("\n--- Registar doença ---")

    nome = pedir_texto("Nome da doença: ")
    descricao = pedir_texto("Descrição da doença: ", obrigatorio=False) or None

    conn.execute(
        """
        INSERT INTO doencas (nome, descricao, consulta_id)
        VALUES (?, ?, ?)
        """,
        (nome, descricao, consulta_id)
    )

    print("Doença registada com sucesso.")


def registar_consulta(conn):
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


def registar_vacina(conn):
    print("\n--- Registar vacina ---")
    animal = escolher_animal(conn)
    if not animal:
        return
    print(f"Animal: {animal['nome']} ({animal['especie']})")
    nome_vacina = pedir_texto("Nome da vacina (ex: Raiva, Polivalente): ")
    
    print("Data de administração (deixa vazio para hoje):")
    data_admin = pedir_data("Data (DD-MM-AAAA): ") or date.today().isoformat()
    proxima_dose = pedir_data("Data da próxima dose / reforço (DD-MM-AAAA, opcional): ")
    lote = pedir_texto("Número de lote (opcional): ", obrigatorio=False) or None
    notas = pedir_texto("Notas (opcional): ", obrigatorio=False) or None

    with conn:
        conn.execute(
            """INSERT INTO vacinas
               (animal_id, nome, data_administracao, proxima_dose, lote, notas)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (animal["id"], nome_vacina, data_admin, proxima_dose, lote, notas),
        )
    print("Vacina registada com sucesso.")
 
 
def consultar_situacao(conn):
    """Resumo da situação atual do animal: dados, última consulta, vacinas e historial."""
    print("\n--- Situação atual do animal ---")
    a = escolher_animal(conn)
    if not a:
        return
 
    consultas = obter_consultas(conn, a["id"])
    vacinas = obter_vacinas(conn, a["id"])
 
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
    else:
        u = consultas[0]
        print(f"  Data: {formatar_data(u['data'])}")
        print(f"  Motivo: {u['motivo']}")
        print(f"  Diagnóstico: {u['diagnostico'] or '—'}")
        print(f"  Tratamento: {u['tratamento'] or '—'}")

    print("\nHistorial de vacinação:")
    if not vacinas:
        print("  Ainda sem vacinas registadas.")
    else:
        for v in vacinas[:5]:
            prox = f" | Próxima dose: {formatar_data(v['proxima_dose'])}" if v['proxima_dose'] else ""
            lote_str = f" (Lote: {v['lote']})" if v['lote'] else ""
            print(f"  {formatar_data(v['data_administracao'])} - {v['nome']}{lote_str}{prox}")
        if len(vacinas) > 5:
            print(f"  ... e mais {len(vacinas) - 5} anterior(es).")
 
    print(f"\nHistorial de consultas ({len(consultas)} consulta(s), mais recentes primeiro):")
    for c in consultas[:5]:
        print(f"  {formatar_data(c['data'])} - {c['motivo']}")
    if len(consultas) > 5:
        print(f"  ... e mais {len(consultas) - 5} anterior(es).")
 
 
def nome_ficheiro_seguro(texto):
    """'João Pedro' -> 'Joao_Pedro' (sem acentos nem caracteres problemáticos)."""
    sem_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9_-]+", "_", sem_acentos).strip("_") or "animal"
 
 
def exportar_pdf(conn):
    """Gera um PDF com a ficha completa do animal, consultas e vacinas."""
    print("\n--- Exportar ficha em PDF ---")
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError:
        print("Falta a biblioteca reportlab. Instala com: pip install reportlab")
        return
 
    a = escolher_animal(conn)
    if not a:
        return
    consultas = obter_consultas(conn, a["id"])
    vacinas = obter_vacinas(conn, a["id"])
 
    def texto(valor):
        """Texto seguro para Paragraph: escapa <, > e & e preserva quebras de linha."""
        return escape(str(valor)).replace("\n", "<br/>") if valor else "—"
 
    cor_principal = colors.HexColor("#1F4E5F")
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle("Titulo", parent=estilos["Title"], textColor=cor_principal,
                                   alignment=0, fontSize=22, spaceAfter=2)
    estilo_sub = ParagraphStyle("Sub", parent=estilos["Normal"], textColor=colors.grey, fontSize=10)
    estilo_sec = ParagraphStyle("Sec", parent=estilos["Heading2"], textColor=cor_principal,
                                spaceBefore=14, spaceAfter=6)
    estilo_cel = ParagraphStyle("Cel", parent=estilos["Normal"], fontSize=9, leading=12)
    estilo_rotulo = ParagraphStyle("Rotulo", parent=estilo_cel, fontName="Helvetica-Bold",
                                   textColor=cor_principal)
    estilo_cab = ParagraphStyle("Cab", parent=estilo_cel, fontName="Helvetica-Bold",
                                textColor=colors.white)
 
    peso = f"{a['peso_kg']} kg" if a["peso_kg"] else None
    dados = [
        ("Nome", a["nome"]),
        ("Espécie", a["especie"]),
        ("Raça", a["raca"]),
        ("Sexo", a["sexo"]),
        ("Data de nascimento", formatar_data(a["data_nascimento"]) if a["data_nascimento"] else None),
        ("Idade", calcular_idade(a["data_nascimento"]) if a["data_nascimento"] else None),
        ("Peso atual", peso),
        ("Dono", a["dono_nome"]),
        ("Contacto do dono", a["dono_contacto"]),
        ("Inscrito em", formatar_data(a["data_inscricao"])),
    ]
    tabela_dados = Table(
        [[Paragraph(r, estilo_rotulo), Paragraph(texto(v), estilo_cel)] for r, v in dados],
        colWidths=[4.5 * cm, 12.5 * cm],
    )
    tabela_dados.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.whitesmoke, colors.white]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
 
    story = [
        Paragraph("Ficha do Animal", estilo_titulo),
        Paragraph(f"{texto(a['nome'])} · ID {a['id']}", estilo_sub),
        Spacer(1, 10),
        Paragraph("Dados gerais", estilo_sec),
        tabela_dados,
        Paragraph("Notas gerais", estilo_sec),
        Paragraph(texto(a["notas"]), estilo_cel),
        Paragraph(f"Historial de vacinação ({len(vacinas)})", estilo_sec),
    ]

    # Tabela de Vacinas
    if vacinas:
        linhas_vac = [[Paragraph(c, estilo_cab) for c in
                       ("Data", "Vacina", "Próxima Dose", "Lote", "Notas")]]
        for v in vacinas:
            linhas_vac.append([
                Paragraph(formatar_data(v["data_administracao"]), estilo_cel),
                Paragraph(texto(v["nome"]), estilo_cel),
                Paragraph(formatar_data(v["proxima_dose"]) if v["proxima_dose"] else "—", estilo_cel),
                Paragraph(texto(v["lote"]), estilo_cel),
                Paragraph(texto(v["notas"]), estilo_cel),
            ])
        tabela_vacinas = Table(
            linhas_vac,
            colWidths=[2.3 * cm, 4.0 * cm, 3.0 * cm, 3.0 * cm, 4.7 * cm],
            repeatRows=1,
        )
        tabela_vacinas.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), cor_principal),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tabela_vacinas)
    else:
        story.append(Paragraph("Ainda sem vacinas registadas.", estilo_cel))

    story.append(Paragraph(f"Historial de consultas ({len(consultas)})", estilo_sec))
 
    if consultas:
        linhas = [[Paragraph(c, estilo_cab) for c in
                   ("Data", "Motivo", "Diagnóstico", "Tratamento", "Peso")]]
        for c in consultas:
            linhas.append([
                Paragraph(formatar_data(c["data"]), estilo_cel),
                Paragraph(texto(c["motivo"]), estilo_cel),
                Paragraph(texto(c["diagnostico"]), estilo_cel),
                Paragraph(texto(c["tratamento"]), estilo_cel),
                Paragraph(f"{c['peso_kg']} kg" if c["peso_kg"] else "—", estilo_cel),
            ])
        tabela_consultas = Table(
            linhas,
            colWidths=[2.3 * cm, 4.0 * cm, 4.5 * cm, 4.5 * cm, 1.7 * cm],
            repeatRows=1,
        )
        tabela_consultas.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), cor_principal),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tabela_consultas)
    else:
        story.append(Paragraph("Ainda sem consultas registadas.", estilo_cel))
 
    def rodape(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(2 * cm, 1.2 * cm,
                          f"Clínica Veterinária · gerado em {date.today().strftime('%d-%m-%Y')}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
        canvas.restoreState()
 
    ficheiro = f"ficha_{nome_ficheiro_seguro(a['nome'])}_{a['id']}.pdf"
    doc = SimpleDocTemplate(
        ficheiro, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
        title=f"Ficha de {a['nome']}", author="Clínica Veterinária",
    )
    try:
        doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    except OSError as erro:
        print(f"Não foi possível gravar o PDF: {erro}")
        return
    print(f"PDF criado: {os.path.abspath(ficheiro)}")
 

def atualizar_esquema(conn):
    """Acrescenta colunas que faltem em bases de dados criadas por versões antigas."""
    colunas = {linha["name"] for linha in conn.execute("PRAGMA table_info(donos)")}
    if "contacto" not in colunas:
        with conn:
            conn.execute("ALTER TABLE donos ADD COLUMN contacto TEXT NOT NULL DEFAULT ''")

# ---------- Menu ----------
 
def menu():
    conn = ligar()
    criar_tabelas(conn)
    atualizar_esquema(conn)
    importar_json(conn)
    try:
        while True:
            print("\n===== Clínica Veterinária =====")
            print("1. Registar animal")
            print("2. Listar animais")
            print("3. Pesquisar")
            print("4. Registar consulta")
            print("5. Registar vacina")
            print("6. Consultar situação atual de um animal")
            print("7. Exportar ficha de um animal em PDF")
            print("0. Sair")
            opcao = input("Opção: ").strip()
 
            if opcao == "1":
                registar_animal(conn)
            elif opcao == "2":
                listar_animais(conn)
            elif opcao == "3":
                pesquisar_animais(conn)
            elif opcao == "4":
                registar_consultas_op = registar_consulta(conn) # Mantém chamada normal
            elif opcao == "5":
                registar_vacina(conn)
            elif opcao == "6":
                consultar_situacao(conn)
            elif opcao == "7":
                exportar_pdf(conn)
            elif opcao == "0":
                print("Até logo!")
                break
            else:
                print("Opção inválida.")
    finally:
        conn.close()
 
 
if __name__ == "__main__":
    menu()