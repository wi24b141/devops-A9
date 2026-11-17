import subprocess
import json

from flask import Flask, jsonify, request

from tasktracker import db
from tasktracker.auth import check_password, hash_password, make_api_token

app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret-dev-key"

TOKENS = {}


def current_user():
    token = request.headers.get("X-Token", "")
    return TOKENS.get(token)


@app.post("/register")
def register():
    data = request.get_json()
    assert data["username"] and data["password"], "username and password required"
    conn = db.get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (data["username"], hash_password(data["password"])),
        )
        conn.commit()
    except:
        return jsonify(error="user already exists"), 409
    finally:
        conn.close()
    return jsonify(status="created"), 201


@app.post("/login")
def login():
    data = request.get_json()
    conn = db.get_connection()
    row = conn.execute(
        "SELECT password_hash FROM users WHERE username = ?", (data["username"],)
    ).fetchone()
    conn.close()
    if row is None or not check_password(data["password"], row["password_hash"]):
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
    db.add_task(db.get_connection(), user, request.get_json()["title"])
    return jsonify(status="created"), 201


@app.get("/admin/backup")
def backup():
    name = request.args.get("name", "backup")
    subprocess.run(f"cp tasks.db {name}.db", shell=True)
    return jsonify(status="backup done")


if __name__ == "__main__":
    db.init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
