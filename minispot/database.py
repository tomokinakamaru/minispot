from atexit import register
from functools import cache
from os import environ, mkdir
from shutil import rmtree
from sqlite3 import connect
from uuid import uuid4

from tornado.autoreload import add_reload_hook


def get_session_id():
    query = "INSERT INTO session VALUES (?)"
    return _connect().execute(query, [uuid4().hex]).lastrowid


def put_history(*hist):
    query = "INSERT INTO history VALUES (?, ?, ?, ?, ?)"
    _connect().execute(query, hist)


@cache
def _connect():
    connection = connect(_path, isolation_level=None)
    connection.execute(_create_session_table_query)
    connection.execute(_create_history_table_query)
    return connection


_create_session_table_query = """
CREATE TABLE IF NOT EXISTS session (
    uuid TEXT NOT NULL
)
"""

_create_history_table_query = """
CREATE TABLE IF NOT EXISTS history (
    session INTEGER NOT NULL,
    restart INTEGER NOT NULL,
    excount INTEGER NOT NULL,
    source TEXT NOT NULL,
    trace TEXT
)
"""

_environ_key = "MINISPOT_DATABASE"

_default_path = "minispot.db"

_path = environ.get(_environ_key, _default_path)

_lock = f"{_path}.lock"

try:
    mkdir(_lock)
except FileExistsError:
    print("Failed to lock database")
    exit(1)
else:
    add_reload_hook(lambda: rmtree(_lock, True))
    register(lambda: rmtree(_lock, True))
