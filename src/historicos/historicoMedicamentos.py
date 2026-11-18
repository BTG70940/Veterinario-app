import sqlite3
from db import CAMINHO_BD, obter_id_animais_por_dono

def obter_medicamentos_por_animal(caminho_bd, animal_id):
    """
    Devolve os medicamentos associados a um animal.

    Parâmetros:
        caminho_bd (str): caminho para o ficheiro da base de dados SQLite.
        animal_id (int): id do animal (campo id_animal).

    Retorna:
        list[dict]: lista de medicamentos, cada um com os campos
                    id, nome_medicamento, quantidade e id_animal.
    """
    print(f"Obtendo medicamentos para o animal com ID: {animal_id}")
    if animal_id is None:
        return []
    if len(animal_id) > 1:
        print(f"Mais de um animal encontrado para o dono logado")

        # Usando apenas o primeiro animal encontrado por enquanto

        animal_id = animal_id[0]

    conn = sqlite3.connect(caminho_bd)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, nome_medicamento, quantidade
            FROM medicamentos
            WHERE id_animal = ?
            """,
            (animal_id,),
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