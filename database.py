"""All database access for the favourites store.

Every SQL statement in the project lives here. Callers pass intent - a search
term, a date range, an availability flag - and never see SQL.
"""

import sqlite3


def connect(path: str = "favourites.db") -> tuple[sqlite3.Connection, sqlite3.Cursor]:
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    return connection, cursor


def create_schema(cursor: sqlite3.Cursor) -> None:
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favourites (
            id INTEGER PRIMARY KEY,
            link TEXT NOT NULL,
            saved_at TEXT,
            available INTEGER,
            checked_at TEXT,
            title TEXT,
            author TEXT,
            thumbnail TEXT
        )
    """)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_favourites_link
        ON favourites (link)
    """)


def _build_filter(
    search: str,
    available_only: bool,
    since: str = "",
    until: str = "",
) -> tuple[str, list]:
    """Return a WHERE clause and the values for its placeholders.

    Shared by the count and the fetch so the two can never disagree about
    which rows match.
    """
    conditions = ["(COALESCE(author, '') LIKE ? OR COALESCE(title, '') LIKE ?)"]
    pattern = f"%{search}%"
    params = [pattern, pattern]

    if available_only:
        conditions.append("available = 1")

    if since:
        conditions.append("saved_at >= ?")
        params.append(since)

    if until:
        # saved_at holds a timestamp, so a bare date would exclude that day.
        conditions.append("saved_at <= ?")
        params.append(f"{until} 23:59:59")

    return " AND ".join(conditions), params


def count_favourites(
    cursor: sqlite3.Cursor,
    search: str = "",
    available_only: bool = False,
    since: str = "",
    until: str = "",
) -> int:
    where_clause, params = _build_filter(search, available_only, since, until)
    query = f"SELECT COUNT(*) FROM favourites WHERE {where_clause}"
    return cursor.execute(query, tuple(params)).fetchone()[0]


def fetch_favourites(
    cursor: sqlite3.Cursor,
    search: str = "",
    available_only: bool = False,
    limit: int = 20,
    offset: int = 0,
    since: str = "",
    until: str = "",
) -> list[sqlite3.Row]:
    where_clause, params = _build_filter(search, available_only, since, until)
    query = f"""
        SELECT saved_at, link, author, title, thumbnail
        FROM favourites
        WHERE {where_clause}
        ORDER BY saved_at DESC NULLS LAST
        LIMIT ? OFFSET ?
    """
    return cursor.execute(query, tuple(params + [limit, offset])).fetchall()


def insert_favourites(cursor: sqlite3.Cursor, favourites: list[tuple]) -> int:
    """Insert (link, saved_at) tuples, skipping links already stored.

    Returns the number of rows actually added, so re-importing a newer export
    reports only what was new.
    """
    cursor.executemany(
        "INSERT OR IGNORE INTO favourites (link, saved_at) VALUES (?, ?)",
        favourites,
    )
    return cursor.rowcount


def unchecked_favourites(cursor: sqlite3.Cursor) -> list[sqlite3.Row]:
    """Rows whose availability has never been established.

    NULL means "not looked at yet", which is what makes the availability job
    resumable after an interruption.
    """
    return cursor.execute(
        "SELECT id, link FROM favourites WHERE available IS NULL"
    ).fetchall()


def record_availability(
    cursor: sqlite3.Cursor,
    favourite_id: int,
    available: int,
    checked_at: str,
    title: str | None = None,
    author: str | None = None,
    thumbnail: str | None = None,
) -> None:
    cursor.execute(
        """
        UPDATE favourites
        SET available = ?, checked_at = ?, title = ?, author = ?, thumbnail = ?
        WHERE id = ?
        """,
        (available, checked_at, title, author, thumbnail, favourite_id),
    )
