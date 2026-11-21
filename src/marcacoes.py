"""Marcação de consultas pelo dono autenticado (story 9)."""
from datetime import datetime

import db

FORMATO_BD = "%Y-%m-%d %H:%M"     # como a data/hora é guardada
FORMATO_ECRA = "%d-%m-%Y %H:%M"   # como a data/hora é mostrada


def _escolher_animal_do_dono(dono_id):
    """
    Mostra os animais do dono e pede para escolher um.

    Parâmetros:
        dono_id (int): ID do dono autenticado.

    Retorna:
        sqlite3.Row | None: o animal escolhido, ou None se não houver/for inválido.
    """
    animais = db.consultar(
        "SELECT id, nome, especie FROM animais WHERE dono_id = ? ORDER BY nome",
        (dono_id,),
    )
    if not animais:
        print("Ainda não tens animais registados. Regista primeiro o teu animal.")
        return None
    print("Os teus animais:")
    for a in animais:
        print(f"  [{a['id']}] {a['nome']} ({a['especie']})")
    valor = input("Id do animal: ").strip()
    for a in animais:
        if valor.isdigit() and a["id"] == int(valor):
            return a
    print("Esse animal não existe ou não é teu.")
    return None


def _pedir_data_hora():
    """
    Pede a data (DD-MM-AAAA) e a hora (HH:MM) da consulta.
    Só aceita datas futuras.

    Retorna:
        datetime | None: a data/hora escolhida, ou None se a data ficar vazia.
    """
    while True:
        data = input("Data (DD-MM-AAAA, vazio para cancelar): ").strip()
        if not data:
            return None
        hora = input("Hora (HH:MM): ").strip()
        try:
            quando = datetime.strptime(f"{data} {hora}", "%d-%m-%Y %H:%M")
        except ValueError:
            print("Data ou hora inválida.")
            continue
        if quando <= datetime.now():
            print("A consulta tem de ser marcada para uma data futura.")
            continue
        return quando


def _escolher_medico():
    """
    Deixa escolher um médico veterinário (opcional).

    Retorna:
        int | None: ID do médico, ou None se não houver preferência.
    """
    medicos = db.consultar(
        "SELECT id, nome, especialidade FROM colaboradores WHERE funcao = ? ORDER BY nome",
        (db.FUNCAO_MEDICO,),
    )
    if not medicos:
        return None
    print("Médicos disponíveis:")
    for m in medicos:
        print(f"  [{m['id']}] {m['nome']} ({m['especialidade'] or 'clínica geral'})")
    while True:
        valor = input("Id do médico (vazio = sem preferência): ").strip()
        if not valor:
            return None
        for m in medicos:
            if valor.isdigit() and m["id"] == int(valor):
                return m["id"]
        print("Médico não encontrado.")


def marcar_consulta(dono_id):
    """
    Formulário para marcar uma consulta para um animal do dono.
    Recusa a marcação se o médico ou o animal já tiverem consulta a essa hora.
    """
    print("\n--- Marcar consulta ---")
    animal = _escolher_animal_do_dono(dono_id)
    if not animal:
        return

    while True:
        quando = _pedir_data_hora()
        if quando is None:
            print("Marcação cancelada.")
            return
        medico_id = _escolher_medico()
        data_hora = quando.strftime(FORMATO_BD)

        if medico_id and db.consultar(
            "SELECT 1 FROM marcacoes WHERE colaborador_id = ? AND data_hora = ? "
            "AND estado = 'marcada'",
            (medico_id, data_hora),
        ):
            print("Esse médico já tem uma consulta a essa hora. Escolhe outra hora.")
            continue
        if db.consultar(
            "SELECT 1 FROM marcacoes WHERE animal_id = ? AND data_hora = ? "
            "AND estado = 'marcada'",
            (animal["id"], data_hora),
        ):
            print(f"O {animal['nome']} já tem uma consulta a essa hora.")
            continue
        break

    motivo = input("Motivo da consulta: ").strip()
    while not motivo:
        motivo = input("O motivo é obrigatório. Motivo da consulta: ").strip()

    id_marcacao = db.executar(
        "INSERT INTO marcacoes (animal_id, data_hora, motivo, colaborador_id) "
        "VALUES (?, ?, ?, ?)",
        (animal["id"], data_hora, motivo, medico_id),
    )
    print(
        f"Consulta marcada (n.º {id_marcacao}) para o {animal['nome']} "
        f"em {quando.strftime(FORMATO_ECRA)}."
    )


def _obter_marcacoes(dono_id, so_futuras_ativas=False):
    """
    Devolve as marcações dos animais do dono, ordenadas por data.

    Parâmetros:
        dono_id (int): ID do dono autenticado.
        so_futuras_ativas (bool): se True, só devolve as futuras ainda não canceladas.
    """
    sql = """
        SELECT m.id, m.data_hora, m.motivo, m.estado,
               a.nome AS animal_nome, c.nome AS medico_nome
        FROM marcacoes m
        JOIN animais a ON a.id = m.animal_id
        LEFT JOIN colaboradores c ON c.id = m.colaborador_id
        WHERE a.dono_id = ?
    """
    parametros = [dono_id]
    if so_futuras_ativas:
        sql += " AND m.estado = 'marcada' AND m.data_hora > ?"
        parametros.append(datetime.now().strftime(FORMATO_BD))
    sql += " ORDER BY m.data_hora"
    return db.consultar(sql, parametros)


def _mostrar(marcacoes):
    """Mostra uma lista de marcações, uma por linha."""
    for m in marcacoes:
        quando = datetime.strptime(m["data_hora"], FORMATO_BD).strftime(FORMATO_ECRA)
        print(
            f"  [{m['id']}] {quando} | {m['animal_nome']} | {m['motivo']} | "
            f"médico: {m['medico_nome'] or 'sem preferência'} | {m['estado']}"
        )


def listar_marcacoes(dono_id):
    """Mostra todas as marcações dos animais do dono."""
    marcacoes = _obter_marcacoes(dono_id)
    if not marcacoes:
        print("Não tens consultas marcadas.")
        return
    print("\nAs tuas marcações:")
    _mostrar(marcacoes)


def cancelar_marcacao(dono_id):
    """Cancela uma marcação futura de um animal do dono (não a apaga)."""
    marcacoes = _obter_marcacoes(dono_id, so_futuras_ativas=True)
    if not marcacoes:
        print("Não tens consultas futuras para cancelar.")
        return
    _mostrar(marcacoes)
    valor = input("Id da marcação a cancelar: ").strip()
    if not any(valor.isdigit() and m["id"] == int(valor) for m in marcacoes):
        print("Marcação não encontrada.")
        return
    db.executar("UPDATE marcacoes SET estado = 'cancelada' WHERE id = ?", (int(valor),))
    print("Marcação cancelada.")


def menu_marcacoes(dono_id):
    """Submenu de marcação de consultas."""
    while True:
        print("\n--- Consultas ---")
        print("1. Marcar consulta")
        print("2. Ver as minhas marcações")
        print("3. Cancelar marcação")
        print("0. Voltar")
        opcao = input("Escolhe uma opção: ").strip()

        if opcao == "1":
            marcar_consulta(dono_id)
        elif opcao == "2":
            listar_marcacoes(dono_id)
        elif opcao == "3":
            cancelar_marcacao(dono_id)
        elif opcao == "0":
            break
        else:
            print("Opção inválida.")