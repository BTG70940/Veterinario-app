"""Área de administração da clínica."""
import db


def contar_animais():
    """Mostra quantos animais estão registados na clínica."""
    linhas = db.consultar("SELECT COUNT(*) AS total FROM animais")
    total = linhas[0]["total"]
    if total == 1:
        print("Há 1 animal registado.")
    else:
        print(f"Há {total} animais registados.")
