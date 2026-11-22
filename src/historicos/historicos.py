import sqlite3
from db import obter_id_animais_por_dono, obter_medicamentos_por_animal, obter_doencas_por_animal

def mostrar_medicamentos(USER_LOGADO):
    """
    Apresenta os medicamentos associados aos animais do dono autenticado.

    Obtém os identificadores dos animais pertencentes ao utilizador
    autenticado e consulta os respetivos medicamentos na base de dados.
    Os medicamentos são agrupados por animal e apresentados no ecrã,
    incluindo o nome do medicamento e a respetiva quantidade.

    Caso o utilizador não tenha animais registados ou nenhum dos seus
    animais esteja a tomar medicação, apresenta uma mensagem informativa.

    :param USER_LOGADO: Identificador do utilizador atualmente autenticado.
    :type USER_LOGADO: int
    :return: Não devolve nenhum valor. Apresenta os medicamentos
             dos animais no terminal.
    :rtype: None
    """
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
    """
    Apresenta o histórico de doenças dos animais pertencentes ao dono autenticado.

    Obtém os identificadores dos animais associados ao utilizador
    autenticado e consulta as respetivas doenças registadas na base
    de dados. As doenças são agrupadas por animal e apresentadas
    no ecrã, incluindo o nome, a descrição, a data do diagnóstico
    e o identificador da consulta associada.

    Caso o utilizador não tenha animais registados ou não existam
    doenças associadas aos seus animais, apresenta uma mensagem
    informativa.

    :param USER_LOGADO: Identificador do utilizador atualmente autenticado.
    :type USER_LOGADO: int
    :return: Não devolve nenhum valor. Apresenta o histórico de doenças
             dos animais no terminal.
    :rtype: None
    """

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