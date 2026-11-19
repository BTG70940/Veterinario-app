"""Área de administração da clínica: animais, donos, fornecedores e produtos."""
import getpass
import hashlib
import hmac
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


# ---------- Produtos ----------

def _pedir_fornecedor(atual=None):
    """Pede o id de um fornecedor existente. Vazio mantém o valor atual (ou nenhum)."""
    if not db.consultar("SELECT 1 FROM fornecedores"):
        return atual
    listar_fornecedores()
    while True:
        valor = input("Id do fornecedor (vazio para manter/nenhum): ").strip()
        if not valor:
            return atual
        if valor.isdigit() and db.consultar(
            "SELECT 1 FROM fornecedores WHERE id = ?", (int(valor),)
        ):
            return int(valor)
        print("Fornecedor não encontrado.")


def listar_produtos():
    """Mostra os produtos e devolve a lista."""
    linhas = db.consultar(
        """
        SELECT p.*, f.nome AS fornecedor_nome
        FROM produtos p
        LEFT JOIN fornecedores f ON f.id = p.fornecedor_id
        ORDER BY p.nome
        """
    )
    if not linhas:
        print("Ainda não há produtos registados.")
        return []
    for p in linhas:
        print(
            f"[{p['id']}] {p['nome']} | {p['categoria'] or '—'} | "
            f"{p['preco']:.2f} € | stock: {p['stock']} | "
            f"fornecedor: {p['fornecedor_nome'] or '—'}"
        )
    return linhas


def registar_produto():
    """Regista um novo produto."""
    print("\n--- Novo produto ---")
    nome = animais.pedir_texto("Nome: ")
    categoria = animais.pedir_texto("Categoria (opcional): ", obrigatorio=False) or None
    preco = _pedir_numero("Preço em €: ", float)
    stock = _pedir_numero("Quantidade em stock: ", int)
    fornecedor_id = _pedir_fornecedor()
    id_p = db.executar(
        "INSERT INTO produtos (nome, categoria, preco, stock, fornecedor_id) "
        "VALUES (?, ?, ?, ?, ?)",
        (nome, categoria, preco, stock, fornecedor_id),
    )
    print(f"Produto registado com o id {id_p}.")


def atualizar_produto():
    """Altera os dados de um produto."""
    if not listar_produtos():
        return
    id_p = _pedir_id("Id do produto a atualizar: ")
    linhas = db.consultar("SELECT * FROM produtos WHERE id = ?", (id_p,)) if id_p else []
    if not linhas:
        print("Produto não encontrado.")
        return
    p = linhas[0]
    print("Deixa em branco para manter o valor atual.")
    nome = input(f"Nome [{p['nome']}]: ").strip() or p["nome"]
    categoria = input(f"Categoria [{p['categoria'] or '—'}]: ").strip() or p["categoria"]
    preco = _pedir_numero(f"Preço em € [{p['preco']:.2f}]: ", float, p["preco"])
    stock = _pedir_numero(f"Stock [{p['stock']}]: ", int, p["stock"])
    fornecedor_id = _pedir_fornecedor(p["fornecedor_id"])
    db.executar(
        "UPDATE produtos SET nome = ?, categoria = ?, preco = ?, stock = ?, "
        "fornecedor_id = ? WHERE id = ?",
        (nome, categoria, preco, stock, fornecedor_id, p["id"]),
    )
    print("Produto atualizado.")


def eliminar_produto():
    """Elimina um produto."""
    if not listar_produtos():
        return
    id_p = _pedir_id("Id do produto a eliminar: ")
    linhas = db.consultar("SELECT * FROM produtos WHERE id = ?", (id_p,)) if id_p else []
    if not linhas:
        print("Produto não encontrado.")
        return
    if input(f"Eliminar '{linhas[0]['nome']}'? (s/n): ").strip().lower() != "s":
        print("Cancelado.")
        return
    db.executar("DELETE FROM produtos WHERE id = ?", (id_p,))
    print("Produto eliminado.")


def menu_produtos():
    """Submenu de gestão de produtos."""
    while True:
        print("\n--- Produtos ---")
        print("1. Registar produto")
        print("2. Listar produtos")
        print("3. Atualizar produto")
        print("4. Eliminar produto")
        print("0. Voltar")
        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            registar_produto()
        elif opcao == "2":
            listar_produtos()
        elif opcao == "3":
            atualizar_produto()
        elif opcao == "4":
            eliminar_produto()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


# ---------- Menu ----------

def menu_administracao():
    """Menu da área de administração."""
    criar_tabelas_admin()
    if not verificar_admin():
        return
    while True:
        print("\n--- Administração ---")
        print("1. Quantos animais estão registados")
        print("2. Listar todos os animais")
        print("3. Pesquisar animais")
        print("4. Listar todos os donos")
        print("5. Gerir fornecedores")
        print("6. Gerir produtos")
        print("0. Voltar")
        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            contar_animais()
        elif opcao == "2":
            listar_todos_animais()
        elif opcao == "3":
            pesquisar_todos_animais()
        elif opcao == "4":
            donos.listar_donos()
        elif opcao == "5":
            menu_fornecedores()
        elif opcao == "6":
            menu_produtos()
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")


# ---------- Acesso restrito ----------

# Hash SHA-256 da palavra-passe de administrador (a palavra-passe em si não é guardada).
HASH_ADMIN = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"


def verificar_admin():
    """Pede a palavra-passe de administrador. Devolve True se estiver correta."""
    for _ in range(3):
        tentativa = getpass.getpass("Palavra-passe de administrador: ")
        hash_tentativa = hashlib.sha256(tentativa.encode()).hexdigest()
        if hmac.compare_digest(hash_tentativa, HASH_ADMIN):
            return True
        print("Palavra-passe incorreta.")
    print("Demasiadas tentativas. Acesso negado.")
    return False
