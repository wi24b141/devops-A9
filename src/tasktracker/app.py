import os
import re
import secrets
import shutil
import sqlite3

from flask import Flask, jsonify, request

from tasktracker import db
from tasktracker.auth import check_password, hash_password, make_api_token

app = Flask(__name__)
# Secret comes from the environment; fall back to a random per-process key for local dev.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

TOKENS = {}
BACKUP_NAME = re.compile(r"[A-Za-z0-9_-]{1,50}")


def current_user():
    token = request.headers.get("X-Token", "")
    return TOKENS.get(token)


@app.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    if not data.get("username") or not data.get("password"):
        return jsonify(error="username and password required"), 400
    conn = db.get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (data["username"], hash_password(data["password"])),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify(error="user already exists"), 409
    finally:
        conn.close()
    return jsonify(status="created"), 201


@app.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    conn = db.get_connection()
    row = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?", (data.get("username"),)
    ).fetchone()
    conn.close()
    if row is None or not check_password(data.get("password", ""), row["password_hash"]):
        return jsonify(error="invalid credentials"), 401
    token = make_api_token()
    TOKENS[token] = data["username"]
    return jsonify(token=token)


@app.get("/tasks")
def list_tasks():
    user = current_user()
    if user is None:
        return jsonify(error="unauthorized"), 401
    conn = db.get_connection()
    rows = db.find_tasks(conn, user, request.args.get("q", ""))
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.post("/tasks")
def create_task():
    user = current_user()
    if user is None:
        return jsonify(error="unauthorized"), 401
    data = request.get_json(silent=True) or {}
    if not data.get("title"):
        return jsonify(error="title required"), 400
    conn = db.get_connection()
    db.add_task(conn, user, data["title"])
    conn.close()
    return jsonify(status="created"), 201


@app.get("/admin/backup")
def backup():
    if current_user() is None:
        return jsonify(error="unauthorized"), 401
    name = request.args.get("name", "backup")
    # Allow-list the file name and copy in Python: no shell, no path traversal.
    if not BACKUP_NAME.fullmatch(name):
        return jsonify(error="invalid backup name"), 400
    shutil.copyfile(db.DB_PATH, f"{name}.db")
    return jsonify(status="backup done")


if __name__ == "__main__":
    db.init_db()
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
        debug=os.environ.get("FLASK_DEBUG") == "1",
    )
