import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Warhammer40K!", # <--- Comma was likely missing here
        database="wargaming_erp",
        autocommit=True,         # <--- Comma here too
        buffered=True
    )