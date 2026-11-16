"""Ponto de entrada da aplicação."""
import db
from menu import menu_principal


def main():
    db.criar_tabelas()
    menu_principal()


if __name__ == "__main__":
    main()
