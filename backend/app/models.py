# scripts/initialize_db.py
import psycopg2

# Import your connection function
from app.database import get_db_connection


DB_NAME = "ECHO_DB"
DB_USER = "myuser"
DB_PASS = "anurag10"
DB_HOST = "localhost"
DB_PORT = "5432"


def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn


def initialize_database():
    # List of SQL commands to create all tables.
    # The order matters due to foreign key dependencies.
    sql_commands = [
        """
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        """,
        """
        CREATE TABLE posts (
            post_id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE comments (
            comment_id SERIAL PRIMARY KEY,
            content TEXT NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            post_id INTEGER NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE,
            parent_id INTEGER REFERENCES comments(comment_id) ON DELETE CASCADE
        );
        """,
        """
        CREATE TABLE categories (
            category_id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL
        );
        """,
        """
        CREATE TABLE follows (
            follower_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            followed_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            PRIMARY KEY (follower_id, followed_id)
        );
        """,
        """
        CREATE TABLE post_likes (
            user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            post_id INTEGER NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, post_id)
        );
        """,
        """
        CREATE TABLE post_categories (
            post_id INTEGER NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE,
            category_id INTEGER NOT NULL REFERENCES categories(category_id) ON DELETE CASCADE,
            PRIMARY KEY (post_id, category_id)
        );
        """,
        """
        CREATE TABLE post_views (
            view_id SERIAL PRIMARY KEY,
            viewed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            user_id INTEGER REFERENCES users(user_id) ON DELETE SET NULL,
            post_id INTEGER NOT NULL REFERENCES posts(post_id) ON DELETE CASCADE
        );
        """,
        # --- Add Indexes for Performance ---
        """ CREATE INDEX ON posts (user_id); """,
        """ CREATE INDEX ON comments (user_id); """,
        """ CREATE INDEX ON comments (post_id); """,
        """ CREATE INDEX ON post_views (user_id); """,
        """ CREATE INDEX ON post_views (post_id); """
    ]

    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        print("Executing SQL commands...")
        # Execute each command
        for command in sql_commands:
            cur.execute(command)

        cur.close()
        conn.commit()
        print("Database has been initialized successfully!")
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while initializing database:", error)
    finally:
        if conn is not None:
            conn.close()

if __name__ == '__main__':
    print("Starting database initialization...")
    initialize_database()
