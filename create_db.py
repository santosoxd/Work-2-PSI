import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password=""
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE IF NOT EXISTS Projeto_2_breno")

mycursor.execute("SHOW DATABASES")

for x in mycursor:
  print(x)
  

