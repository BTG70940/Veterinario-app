import sqlite3
from db import CAMINHO_BD, obter_id_animais_por_dono

def obter_medicamentos_por_animal(caminho_bd, animal_id):
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

    # Remove IDs None da lista
    animal_id = [id for id in animal_id if id is not None]

    if not animal_id:
        return []

    conn = sqlite3.connect(caminho_bd)

    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        placeholders = ",".join("?" for _ in animal_id)

        cursor.execute(
            f"""
            SELECT id, nome_medicamento, quantidade, id_animal
            FROM medicamentos
            WHERE id_animal IN ({placeholders})
            """,
            tuple(animal_id)
        )

        return [dict(linha) for linha in cursor.fetchall()]

    finally:
        conn.close()


def mostrar_medicamentos(USER_LOGADO):
    # Obter o ID do animal associado ao dono logado
    animal_id = obter_id_animais_por_dono(USER_LOGADO)
    if not animal_id:
        print("Não tem animais registados.")
        return

    medicamentos = obter_medicamentos_por_animal(CAMINHO_BD, animal_id)

    print("==================================================")

    if len(medicamentos) < 1:
        print("Não tem animais a tomar medicação")
    else:
        print(medicamentos)
        
    print("==================================================")