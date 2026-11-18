import sqlite3
from db import obter_id_animais_por_dono, obter_medicamentos_por_animal

def mostrar_medicamentos(USER_LOGADO):
    # Obter o ID do animal associado ao dono logado
    animal_id = obter_id_animais_por_dono(USER_LOGADO)
    if not animal_id:
        print("Não tem animais registados.")
        return

    medicamentos = obter_medicamentos_por_animal(animal_id)

    print("==================================================")

    if len(medicamentos) < 1:
        print("Não tem animais a tomar medicação")
    else:
        print(medicamentos)
        
    print("==================================================")