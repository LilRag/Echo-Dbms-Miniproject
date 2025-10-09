# app/database.py
import mysql.connector 
from mysql.connector import errorcode

DB_USER = "root"
DB_PASSWORD ="anurag10"
DB_HOST = "localhost"
DB_NAME ="ECHO"


def get_db_connection():
    try:
        conn = mysql.connector.connect(
            user = DB_USER,
            password = DB_PASSWORD,
            host = DB_HOST,
            database = DB_NAME
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist ")
        else:
            print(err)
        return None 
    
