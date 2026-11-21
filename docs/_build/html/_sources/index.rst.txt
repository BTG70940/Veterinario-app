Veterinário App
===============

Aplicação em Python, para a consola, que gere uma clínica veterinária:
donos, animais, consultas, vacinas, históricos de doenças e medicamentos,
fornecedores, produtos e colaboradores.

Trabalho prático TP2 do grupo H, na unidade curricular de Ambientes de
Desenvolvimento Colaborativo.

Como executar
-------------

Requer Python 3.10 ou superior. Na pasta principal do projeto::

    pip install reportlab
    python src/main.py

O ``reportlab`` só é necessário para exportar fichas de animais em PDF.
A base de dados SQLite (``veterinario.db``) é criada automaticamente.

Estrutura do código
-------------------

* ``main.py``: ponto de entrada e autenticação (login e registo).
* ``menu.py``: menu principal e navegação entre as áreas.
* ``db.py``: ligação à base de dados e criação das tabelas.
* ``donos.py``: registo, listagem e atualização de donos.
* ``animais.py``: animais, consultas, vacinas e exportação de fichas em PDF.
* ``administracao.py``: área de administração, protegida por palavra-passe.
* ``marcacoes.py``: marcação, listagem e cancelamento de consultas.
* ``historicos/``: histórico de doenças e de medicamentos.

.. toctree::
   :maxdepth: 2
   :caption: Código fonte

   api/modules
