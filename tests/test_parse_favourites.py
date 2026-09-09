import json

from parse_favourites import load_favourites


def write_export(tmp_path, favourites):
    path = tmp_path / "export.json"
    path.write_text(json.dumps({
        "Likes and Favorites": {
            "Favorite Videos": {"FavoriteVideoList": favourites},
        },
    }))
    return path


def test_digs_the_favourites_out_of_the_nesting(tmp_path):
    path = write_export(tmp_path, [{"Date": "2025-01-01 00:00:00", "Link": "https://x/1"}])
    assert load_favourites(path) == [
        {"Date": "2025-01-01 00:00:00", "Link": "https://x/1"}
    ]


def test_returns_an_empty_list_when_there_are_no_favourites(tmp_path):
    path = write_export(tmp_path, [])
    assert load_favourites(path) == []


def test_entries_without_a_date_are_passed_through_untouched(tmp_path):
    path = write_export(tmp_path, [{"Link": "https://x/1"}])
    assert load_favourites(path)[0].get("Date") is None
