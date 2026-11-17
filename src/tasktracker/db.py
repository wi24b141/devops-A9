import sqlite3

DB_PATH = "tasks.db"


def get_connection(path=None):
    conn = sqlite3.connect(path or DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path=None):
    conn = get_connection(path)
    conn.execute(
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "username TEXT UNIQUE NOT NULL, "
        "password_hash TEXT NOT NULL)"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS tasks ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "owner TEXT NOT NULL, "
        "title TEXT NOT NULL, "
        "done INTEGER NOT NULL DEFAULT 0)"
    )
    conn.commit()
    conn.close()


def find_tasks(conn, owner, search=""):
    # Parameterised query: user input is passed as data, never spliced into the SQL text.
    query = "SELECT id, title, done FROM tasks WHERE owner = ? AND title LIKE ?"
    return conn.execute(query, (owner, f"%{search}%")).fetchall()


def add_task(conn, owner, title):
    conn.execute("INSERT INTO tasks (owner, title) VALUES (?, ?)", (owner, title))
    conn.commit()
