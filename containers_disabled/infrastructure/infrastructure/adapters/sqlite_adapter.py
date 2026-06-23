"""SQLite adapter for dockerless database operations."""

import logging
import sqlite3
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class SQLiteAdapter:
    """SQLite database adapter."""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None

    def connect(self):
        """Establish database connection."""
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        return self

    def close(self):
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute SQL query."""
        cursor = self._conn.cursor()
        cursor.execute(query, params)
        return cursor

    def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        """Fetch all results as dictionaries."""
        cursor = self.execute(query, params)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Fetch one result as dictionary."""
        cursor = self.execute(query, params)
        row = cursor.fetchone()
        return dict(row) if row else None

    def commit(self):
        """Commit transaction."""
        if self._conn:
            self._conn.commit()

    def rollback(self):
        """Rollback transaction."""
        if self._conn:
            self._conn.rollback()
