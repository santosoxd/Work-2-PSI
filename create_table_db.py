import sys
sys.path.append('C:/Users/l2457/Desktop/Breno/Projeto')
from connect_db import start_connection

mydb = start_connection()
mycursor = mydb.cursor()

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS filmes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        titulo VARCHAR(100),
        duracao INT,
        classificacao VARCHAR(10)
    )""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS sessoes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filme_id INT,
        horario VARCHAR(20),
        assentos_disponiveis INT,
        FOREIGN KEY (filme_id) REFERENCES filmes(id) ON DELETE CASCADE
    )""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100),
        nif VARCHAR(9) UNIQUE
    )""")

mycursor.execute("""
    CREATE TABLE IF NOT EXISTS ingressos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        cliente_id INT,
        sessao_id INT,
        FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
        FOREIGN KEY (sessao_id) REFERENCES sessoes(id) ON DELETE CASCADE
    )""")
mycursor.execute("SHOW TABLES")

for x in mycursor:
      print(x)