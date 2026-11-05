from typing import Self

import pymysql
import pymysql.cursors


class DorisConnection:
    """
    A simple, dedicated connection class for Apache Doris.
    Connects directly to a catalog.database without manual SWITCH/USE calls.

    Usage:
        db = DorisConnection("localhost", "root", "", "fluss_paimon.mart")
        rows = db.execute("SHOW TABLES")
    """

    def __init__(
        self,
        host: str,
        user: str,
        password: str,
        database: str,
        catalog: str = "internal",
        port: int = 9030,
        charset: str = "utf8mb4",
        autocommit: bool = True,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.catalog = catalog
        self.charset = charset
        self.autocommit = autocommit

        self._conn: pymysql.connections.Connection | None = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------
    @property
    def is_connected(self) -> bool:
        """Public check to see if the connection is active and open."""
        return self._conn is not None and self._conn.open

    def connect(self) -> Self:
        """Open the connection and land directly on the target catalog + db."""
        self._conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            charset=self.charset,
            autocommit=self.autocommit,
            cursorclass=pymysql.cursors.DictCursor,
        )
        # Land on the right catalog then the right database in one shot
        with self._conn.cursor() as cur:
            cur.execute(f"SWITCH `{self.catalog}`")
            cur.execute(f"USE `{self.database}`")
        return self

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def _ensure_connected(self):
        if not self._conn or not self._conn.open:
            self.connect()

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def execute(self, sql: str, params=None) -> list[dict]:
        """Run a SQL statement and return all rows as a list of dicts."""
        self._ensure_connected()
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()

    def execute_one(self, sql: str, params=None) -> dict | None:
        """Run a SQL statement and return a single row (or None)."""
        self._ensure_connected()
        with self._conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()

    def execute_many(self, sql: str, data: list) -> int:
        """Execute a statement for each row in data. Returns affected row count."""
        self._ensure_connected()
        with self._conn.cursor() as cur:
            cur.executemany(sql, data)
            return cur.rowcount

    # ------------------------------------------------------------------
    # Context manager support  (with DorisConnection(...) as db:)
    # ------------------------------------------------------------------

    def __enter__(self) -> Self:
        return self.connect()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    @property
    def full_target(self) -> str:
        return f"{self.catalog}.{self.database}"

    def __repr__(self) -> str:
        status = "open" if self._conn and self._conn.open else "closed"
        return (
            f"DorisConnection({self.host}:{self.port} → {self.full_target} [{status}])"
        )
