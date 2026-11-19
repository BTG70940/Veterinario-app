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


# ---------- Fornecedores ----------

def listar_fornecedores():
    """Mostra os fornecedores e devolve a lista."""
    linhas = db.consultar("SELECT * FROM fornecedores ORDER BY nome")
    if not linhas:
        print("Ainda não há fornecedores registados.")
        return []
    for f in linhas:
        print(f"[{f['id']}] {f['nome']} | {f['contacto'] or '—'} | {f['email'] or '—'}")
    return linhas


def registar_fornecedor():
    """Regista um novo fornecedor."""
    print("\n--- Novo fornecedor ---")
    nome = animais.pedir_texto("Nome: ")
    contacto = animais.pedir_texto("Contacto (opcional): ", obrigatorio=False) or None
    email = animais.pedir_texto("Email (opcional): ", obrigatorio=False) or None
    morada = animais.pedir_texto("Morada (opcional): ", obrigatorio=False) or None
    try:
        id_f = db.executar(
            "INSERT INTO fornecedores (nome, contacto, email, morada) VALUES (?, ?, ?, ?)",
            (nome, contacto, email, morada),
        )
    except sqlite3.IntegrityError:
        print("Já existe um fornecedor com esse nome.")
        return
    print(f"Fornecedor registado com o id {id_f}.")


def atualizar_fornecedor():
    """Altera os dados de um fornecedor."""
    if not listar_fornecedores():
        return
    id_f = _pedir_id("Id do fornecedor a atualizar: ")
    linhas = db.consultar("SELECT * FROM fornecedores WHERE id = ?", (id_f,)) if id_f else []
    if not linhas:
        print("Fornecedor não encontrado.")
        return
    f = linhas[0]
    print("Deixa em branco para manter o valor atual.")
    nome = input(f"Nome [{f['nome']}]: ").strip() or f["nome"]
    contacto = input(f"Contacto [{f['contacto'] or '—'}]: ").strip() or f["contacto"]
    email = input(f"Email [{f['email'] or '—'}]: ").strip() or f["email"]
    morada = input(f"Morada [{f['morada'] or '—'}]: ").strip() or f["morada"]
    try:
        db.executar(
            "UPDATE fornecedores SET nome = ?, contacto = ?, email = ?, morada = ? WHERE id = ?",
            (nome, contacto, email, morada, f["id"]),
        )
    except sqlite3.IntegrityError:
        print("Já existe outro fornecedor com esse nome.")
        return
    print("Fornecedor atualizado.")


def eliminar_fornecedor():
    """Elimina um fornecedor (se não tiver produtos associados)."""
    if not listar_fornecedores():
        return
    id_f = _pedir_id("Id do fornecedor a eliminar: ")
    linhas = db.consultar("SELECT * FROM fornecedores WHERE id = ?", (id_f,)) if id_f else []
    if not linhas:
        print("Fornecedor não encontrado.")
        return
    if input(f"Eliminar '{linhas[0]['nome']}'? (s/n): ").strip().lower() != "s":
        print("Cancelado.")
        return
    try:
        db.executar("DELETE FROM fornecedores WHERE id = ?", (id_f,))
    except sqlite3.IntegrityError:
        print("Não é possível eliminar: o fornecedor tem produtos associados.")
        return
    print("Fornecedor eliminado.")


def menu_fornecedores():
    """Submenu de gestão de fornecedores."""
    while True:
        print("\n--- Fornecedores ---")
        print("1. Registar fornecedor")
        print("2. Listar fornecedores")
        print("3. Atualizar fornecedor")
        print("4. Eliminar fornecedor")
        print("0. Voltar")
        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            registar_fornecedor()
        elif opcao == "2":
            listar_fornecedores()
        elif opcao == "3":
            atualizar_fornecedor()
        elif opcao == "4":
            eliminar_fornecedor()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")
