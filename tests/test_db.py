from tasktracker import db


def _setup(tmp_path):
    path = str(tmp_path / "test.db")
    db.init_db(path)
    conn = db.get_connection(path)
    db.add_task(conn, "alice", "write report")
    db.add_task(conn, "bob", "bob's secret task")
    return conn


def test_add_and_find_task(tmp_path):
    conn = _setup(tmp_path)
    rows = db.find_tasks(conn, "alice", "report")
    assert len(rows) == 1
    assert rows[0]["title"] == "write report"


def test_search_is_not_sql_injectable(tmp_path):
    # Regression test for flake8-bandit S608: this payload used to return every user's tasks.
    conn = _setup(tmp_path)
    rows = db.find_tasks(conn, "alice", "%' OR owner LIKE '%")
    assert [r["title"] for r in rows] == []
