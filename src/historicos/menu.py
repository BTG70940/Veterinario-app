from .historicoMedicamentos import obter_medicamentos_por_animal
from db import CAMINHO_BD

def menu_medicamentos():
    while True:
        print("\n=== Menu de Historicos ===")
        print("1. Medicamentos")
        print("0. Voltar")

        escolha = input("Escolha uma opção: ").strip()

        if escolha == "1":
            obter_medicamentos_por_animal()
            
        elif escolha == "0":
            print("A voltar...")
            break
        else:
            print("Opção inválida. Tenta novamente.")
