import mysql.connector

def start_connection():
    return mysql.connector.connect(
      host="localhost",
      user="root",
      password="",
      database="Projeto_2_breno"
    )