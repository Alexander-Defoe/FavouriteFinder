from database import _build_filter, connect, count_favourites, create_schema


def test_search_term_is_wrapped_for_like_matching():
    _, params = _build_filter("x", False)
    assert params == ["%x%", "%x%"]


def test_no_availability_condition_by_default():
    where_clause, _ = _build_filter("x", False)
    assert "available" not in where_clause


def test_availability_flag_adds_its_condition():
    where_clause, _ = _build_filter("x", True)
    assert "available = 1" in where_clause


def test_availability_flag_adds_no_parameter():
    _, params = _build_filter("x", True)
    assert len(params) == 2


def test_end_date_is_made_inclusive():
    _, params = _build_filter("x", False, until="2025-01-01")
    assert params[-1] == "2025-01-01 23:59:59"


def test_every_placeholder_has_a_parameter():
    combinations = [
        ("", False, "", ""),
        ("pasta", True, "", ""),
        ("pasta", False, "2025-01-01", ""),
        ("pasta", True, "2025-01-01", "2025-12-31"),
    ]
    for search, available_only, since, until in combinations:
        where_clause, params = _build_filter(search, available_only, since, until)
        assert where_clause.count("?") == len(params)

def make_database(tmp_path):
    connection, cursor = connect(tmp_path / "test.db")
    create_schema(cursor)
    rows = [
        ("https://x/1", "2025-01-15 10:00:00", 1, "Zach", "pasta recipe"),
        ("https://x/2", "2024-06-01 10:00:00", 0, None, None),
        ("https://x/3", "2026-03-10 10:00:00", 1, "Ruby", "poetry"),
    ]
    cursor.executemany(
        "INSERT INTO favourites (link, saved_at, available, author, title)"
        " VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    connection.commit()
    return cursor


def make_database(tmp_path):
    connection, cursor = connect(tmp_path / "test.db")
    create_schema(cursor)
    rows = [
        ("https://x/1", "2025-01-15 10:00:00", 1, "Zach", "pasta recipe"),
        ("https://x/2", "2024-06-01 10:00:00", 0, None, None),
        ("https://x/3", "2026-03-10 10:00:00", 1, "Ruby", "poetry"),
    ]
    cursor.executemany(
        "INSERT INTO favourites (link, saved_at, available, author, title)"
        " VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    connection.commit()
    return cursor


def test_counts_every_row_by_default(tmp_path):
    cursor = make_database(tmp_path)
    assert count_favourites(cursor) == 3


def test_search_matches_a_single_author(tmp_path):
    cursor = make_database(tmp_path)
    assert count_favourites(cursor, search="zach") == 1


def test_availability_flag_excludes_dead_rows(tmp_path):
    cursor = make_database(tmp_path)
    assert count_favourites(cursor, available_only=True) == 2


def test_since_excludes_older_rows(tmp_path):
    cursor = make_database(tmp_path)
    assert count_favourites(cursor, since="2025-01-01") == 2
