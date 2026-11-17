import pytest

from tasktracker import app as app_module
from tasktracker import db


@pytest.fixture
def client(tmp_path, monkeypatch):
    path = str(tmp_path / "app.db")
    monkeypatch.setattr(db, "DB_PATH", path)
    monkeypatch.chdir(tmp_path)
    db.init_db(path)
    return app_module.app.test_client()


def _login(client):
    client.post("/register", json={"username": "alice", "password": "pw"})
    token = client.post("/login", json={"username": "alice", "password": "pw"}).json["token"]
    return {"X-Token": token}


def test_register_requires_fields(client):
    assert client.post("/register", json={}).status_code == 400


def test_duplicate_user_returns_409(client):
    client.post("/register", json={"username": "bob", "password": "pw"})
    assert client.post("/register", json={"username": "bob", "password": "pw"}).status_code == 409


def test_backup_rejects_shell_injection(client):
    headers = _login(client)
    resp = client.get("/admin/backup?name=x;rm -rf ~", headers=headers)
    assert resp.status_code == 400


def test_backup_requires_login(client):
    assert client.get("/admin/backup").status_code == 401
