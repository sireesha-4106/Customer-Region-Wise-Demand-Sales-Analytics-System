import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Siri4106@",
    database="rinl_sales"
)

print("Connected Successfully")