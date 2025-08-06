import sqlite3
import pytest
from crypto_analyzer.models.database import Database


@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / 'test.db'))
    yield database
    database.close()


def test_connection(db):
    conn1 = db.connect()
    assert isinstance(conn1, sqlite3.Connection)
    conn2 = db.connect()
    assert conn1 is conn2
    db.close()
    assert db._conn is None


def test_crud_operations(db):
    db.create_table('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')

    db.insert('test', {'id': 1, 'name': 'alpha'})
    rows = db.select('test')
    assert rows == [(1, 'alpha')]

    db.update('test', {'name': 'beta'}, 'id=?', (1,))
    rows = db.select('test', 'id=?', (1,))
    assert rows == [(1, 'beta')]

    db.delete('test', 'id=?', (1,))
    rows = db.select('test')
    assert rows == []
