import sqlite3
from db import CAMINHO_BD

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
    conn = sqlite3.connect(caminho_bd)
    try:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, nome_medicamento, quantidade, id_animal
            FROM medicamentos
            WHERE id_animal = ?
            """,
            (animal_id,),
        )
        return [dict(linha) for linha in cursor.fetchall()]
    finally:
        conn.close()

def mostrar_medicamentos():
    medicamentos = obter_medicamentos_por_animal(CAMINHO_BD, 1)

    print("==================================================")

    if len(medicamentos) < 1:
        print("Não tem animais a tomar medicação")
    else:
        print(medicamentos)
        
    print("==================================================")