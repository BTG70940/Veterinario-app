import sqlite3
from db import obter_id_animais_por_dono, obter_medicamentos_por_animal, obter_doencas_por_animal

def mostrar_medicamentos(USER_LOGADO):
    # Obter o ID do animal associado ao dono logado
    animal_id = obter_id_animais_por_dono(USER_LOGADO)
    if not animal_id:
        print("Não tem animais registados.")
        return

    medicamentos = obter_medicamentos_por_animal(animal_id)

    print("\n" + "=" * 45)
    print("          MEDICAMENTOS DOS ANIMAIS")
    print("=" * 45)

    if not medicamentos:
        print("\n  Não tem animais a tomar medicação.")
    else:
        # Agrupar medicamentos por animal
        medicamentos_por_animal = {}

        for med in medicamentos:
            id_animal = med["id_animal"]

            if id_animal not in medicamentos_por_animal:
                medicamentos_por_animal[id_animal] = []

            medicamentos_por_animal[id_animal].append(med)

        for id_animal, lista in medicamentos_por_animal.items():
            print(f"\n  MEDICAÇÃO DO ANIMAL: {lista[0]['nome_animal']}")
            print("  " + "-" * 35)

            for med in lista:
                print(f"  Medicamento : {med['nome_medicamento']}")
                print(f"  Quantidade  : {med['quantidade']}")
                print()

    print("=" * 45)


def mostrar_historico_doencas(USER_LOGADO):
    """Mostra o histórico de doenças dos animais do dono autenticado."""

    animal_id = obter_id_animais_por_dono(USER_LOGADO)

    if not animal_id:
        print("Não tem animais registados.")
        return

    doencas = obter_doencas_por_animal(animal_id)

    print("\n" + "=" * 45)
    print("          HISTÓRICO DE DOENÇAS")
    print("=" * 45)

    if not doencas:
        print("\n  Não existem doenças registadas.")
    else:
        # Agrupar doenças por animal
        doencas_por_animal = {}

        for doenca in doencas:
            id_animal = doenca["id_animal"]

            if id_animal not in doencas_por_animal:
                doencas_por_animal[id_animal] = []

            doencas_por_animal[id_animal].append(doenca)

        for id_animal, lista in doencas_por_animal.items():

            print(f"\n  HISTÓRICO DO ANIMAL: {lista[0]['nome_animal']}")
            print("  " + "-" * 35)

            for doenca in lista:
                print(f"  Doença            : {doenca['nome']}")
                print(f"  Descrição         : {doenca['descricao'] or 'Sem descrição'}")
                print(f"  Data diagnóstico  : {doenca['data']}")
                print(f"  Consulta ID       : {doenca['consulta_id']}")
                print()

    print("=" * 45)