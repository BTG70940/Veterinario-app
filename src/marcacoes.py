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