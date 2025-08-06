"""Simple SQLite database layer with basic CRUD helpers."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, Iterable, Optional


class Database:
    """Lightweight wrapper around sqlite3 providing helper methods."""

    def __init__(self, path: str) -> None:
        self.path = path
        self._conn: Optional[sqlite3.Connection] = None

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------
    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
            self._conn = sqlite3.connect(self.path, check_same_thread=False)
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    @contextmanager
    def cursor(self):
        conn = self.connect()
        cur = conn.cursor()
        try:
            yield cur
            conn.commit()
        finally:
            cur.close()

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------
    def execute(self, sql: str, params: Iterable[Any] = ()):
        with self.cursor() as cur:
            cur.execute(sql, params)
            return cur

    def create_table(self, sql: str) -> None:
        self.execute(sql)

    def insert(self, table: str, data: Dict[str, Any], replace: bool = False) -> None:
        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" for _ in data)
        command = "INSERT OR REPLACE" if replace else "INSERT"
        sql = f"{command} INTO {table} ({columns}) VALUES ({placeholders})"
        self.execute(sql, tuple(data.values()))

    def select(self, table: str, where: str = "", params: Iterable[Any] = ()):
        sql = f"SELECT * FROM {table}"
        if where:
            sql += f" WHERE {where}"
        with self.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def update(self, table: str, data: Dict[str, Any], where: str = "", params: Iterable[Any] = ()) -> None:
        set_clause = ", ".join(f"{col}=?" for col in data)
        sql = f"UPDATE {table} SET {set_clause}"
        if where:
            sql += f" WHERE {where}"
        values = list(data.values()) + list(params)
        self.execute(sql, values)

    def delete(self, table: str, where: str = "", params: Iterable[Any] = ()) -> None:
        sql = f"DELETE FROM {table}"
        if where:
            sql += f" WHERE {where}"
        self.execute(sql, params)
