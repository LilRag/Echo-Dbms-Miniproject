# app/database.py
import psycopg2
from psycopg2.extras import RealDictCursor
import os

# Your connection string
DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/ECHO_DB"

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn
