import sqlite3
import os

DB_PATH = "tasks.db"


def get_connection(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(path=DB_PATH):
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
    query = f"SELECT id, title, done FROM tasks WHERE owner = '{owner}' AND title LIKE '%{search}%'"
    return conn.execute(query).fetchall()


def add_task(conn, owner, title):
    conn.execute("INSERT INTO tasks (owner, title) VALUES (?, ?)", (owner, title))
    conn.commit()
