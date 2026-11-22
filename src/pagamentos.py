"""Pagamentos das consultas (área de administração)."""
import sqlite3
from datetime import date

import db

METODOS = ("dinheiro", "multibanco", "MB Way")


def criar_tabela_pagamentos():
    """Cria a tabela de pagamentos, caso ainda não exista."""
    db.executar(
        """
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consulta_id INTEGER NOT NULL
                REFERENCES consultas(id) ON DELETE CASCADE,
            valor REAL NOT NULL CHECK (valor > 0),
            data TEXT NOT NULL,
            metodo TEXT NOT NULL
                CHECK (metodo IN ('dinheiro', 'multibanco', 'MB Way'))
        )
        """
    )


def _formatar_data(iso):
    """Converte AAAA-MM-DD em DD-MM-AAAA."""
    return date.fromisoformat(iso).strftime("%d-%m-%Y")


def _pedir_valor():
    """Pede um valor em euros maior que zero."""
    while True:
        texto = input("Valor em €: ").strip().replace(",", ".")
        try:
            valor = float(texto)
        except ValueError:
            valor = 0
        if valor > 0:
            return round(valor, 2)
        print("Valor inválido. Escreve um número maior que 0.")


def _pedir_metodo():
    """Pede o método de pagamento e devolve o nome escolhido."""
    while True:
        for i, metodo in enumerate(METODOS, start=1):
            print(f"  {i}. {metodo}")
        escolha = input("Método de pagamento: ").strip()
        if escolha.isdigit() and 1 <= int(escolha) <= len(METODOS):
            return METODOS[int(escolha) - 1]
        print("Opção inválida.")


def _consultas_por_pagar():
    """Devolve as consultas sem pagamento (lista vazia se não houver)."""
    try:
        return db.consultar(
            """
            SELECT c.id, c.data, c.motivo, a.nome AS animal, d.nome AS dono
            FROM consultas c
            JOIN animais a ON a.id = c.animal_id
            JOIN donos d ON d.id = a.dono_id
            WHERE NOT EXISTS (SELECT 1 FROM pagamentos p WHERE p.consulta_id = c.id)
            ORDER BY c.data DESC, c.id DESC
            """
        )
    except sqlite3.OperationalError:
        return []


def registar_pagamento():
    """Regista o pagamento de uma consulta que ainda não foi paga."""
    consultas = _consultas_por_pagar()
    if not consultas:
        print("Não há consultas por pagar.")
        return
    print("\n--- Consultas por pagar ---")
    for c in consultas:
        print(
            f"[{c['id']}] {_formatar_data(c['data'])} | {c['animal']} "
            f"(dono: {c['dono']}) | {c['motivo']}"
        )
    escolha = input("Id da consulta: ").strip()
    if not escolha.isdigit() or int(escolha) not in {c["id"] for c in consultas}:
        print("Consulta inválida.")
        return
    valor = _pedir_valor()
    metodo = _pedir_metodo()
    db.executar(
        "INSERT INTO pagamentos (consulta_id, valor, data, metodo) VALUES (?, ?, ?, ?)",
        (int(escolha), valor, date.today().isoformat(), metodo),
    )
    print("Pagamento registado.")
