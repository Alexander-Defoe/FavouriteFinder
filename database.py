import sqlite3

def connect(path: str = "favourites.db"):
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    return connection, cursor

def _build_filter(search, available_only, since="", until=""):
    conditions = ["(COALESCE(author, '') LIKE ? OR COALESCE(title, '') LIKE ?)"]
    pattern = f"%{search}%"
    params = [pattern, pattern]

    if available_only:
        conditions.append("available = 1")

    if since:
        conditions.append("saved_at >= ?")
        params.append(since)

    if until:
        conditions.append("saved_at <= ?")
        params.append(f"{until} 23:59:59")

    return " AND ".join(conditions), params

def count_favourites(cursor, search="", available_only=False, since="", until=""):
    where_clause, params = _build_filter(search, available_only, since, until)
    query = f"SELECT COUNT(*) FROM favourites WHERE {where_clause}"
    return cursor.execute(query, tuple(params)).fetchone()[0]


def fetch_favourites(cursor, search="", available_only=False, limit=20, offset=0, since="", until=""):
    where_clause, params = _build_filter(search, available_only, since, until)
    query = f"""
        SELECT saved_at, link, author, title
        FROM favourites
        WHERE {where_clause}
        ORDER BY saved_at DESC NULLS LAST
        LIMIT ? OFFSET ?
    """
    return cursor.execute(query, tuple(params + [limit, offset])).fetchall()