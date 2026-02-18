import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Warhammer40K!", 
        database="wargaming_erp",
        connect_timeout=60,
        buffered=True
    )

