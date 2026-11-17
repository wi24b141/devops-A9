from tasktracker import db


def test_add_and_find_task(tmp_path):
    path = str(tmp_path / "test.db")
    db.init_db(path)
    conn = db.get_connection(path)
    db.add_task(conn, "alice", "write report")
    rows = db.find_tasks(conn, "alice", "report")
    assert len(rows) == 1
    assert rows[0]["title"] == "write report"
