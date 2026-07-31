"""SQLite bootstrap and read-only query adapter."""

from __future__ import annotations

from pathlib import Path
from sqlite3 import Connection, connect


class SalesDatabase:
    def __init__(self, path: Path, data_directory: Path) -> None:
        self.path = path
        self.data_directory = data_directory

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        connection = connect(self.path)
        try:
            connection.executescript(
                (self.data_directory / "schema.sql").read_text(encoding="utf-8")
            )
            count = connection.execute("SELECT COUNT(*) FROM sales_orders").fetchone()[0]
            if count == 0:
                connection.executescript(
                    (self.data_directory / "seed.sql").read_text(encoding="utf-8")
                )
            connection.commit()
        finally:
            connection.close()

    def read_only_connection(self) -> Connection:
        connection = connect(f"file:{self.path.resolve()}?mode=ro", uri=True)
        connection.row_factory = lambda cursor, row: {
            description[0]: row[index]
            for index, description in enumerate(cursor.description)
        }
        return connection
