"""SQLite connection manager."""

import os
import sqlite3

_DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
_DB_PATH = os.path.join(_DB_DIR, "sports_cards.db")

_connection: sqlite3.Connection | None = None


def get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        os.makedirs(_DB_DIR, exist_ok=True)
        _connection = sqlite3.connect(_DB_PATH)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA journal_mode=WAL")
        _connection.execute("PRAGMA foreign_keys=ON")
    return _connection


def close_connection():
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None
