from browse import is_valid_date, last_page_number, shorten


def test_last_page_rounds_up_for_a_partial_final_page():
    assert last_page_number(100, 3) == 34


def test_last_page_adds_no_extra_page_for_an_exact_multiple():
    assert last_page_number(100, 10) == 10


def test_last_page_is_zero_when_there_are_no_items():
    assert last_page_number(0, 20) == 0


def test_shorten_truncates_and_marks_the_cut():
    assert shorten("abcdefghij", 4) == "abc…"


def test_shorten_returns_short_text_unchanged():
    assert shorten("abc", 10) == "abc"


def test_shorten_returns_empty_string_for_none():
    assert shorten(None, 10) == ""


def test_shorten_never_exceeds_the_requested_width():
    assert len(shorten("abcdefghij", 4)) == 4


def test_shorten_at_width_one_returns_only_the_ellipsis():
    assert shorten("abcdefghij", 1) == "…"


def test_shorten_at_width_zero_returns_empty_string():
    assert shorten("abcdefghij", 0) == ""


def test_shorten_leaves_text_of_exactly_the_width_alone():
    assert shorten("abcd", 4) == "abcd"


def test_empty_date_is_valid_because_the_filter_is_optional():
    assert is_valid_date("") is True


def test_a_plain_iso_date_is_valid():
    assert is_valid_date("2025-01-01") is True


def test_a_word_is_not_a_date():
    assert is_valid_date("banana") is False


def test_an_impossible_date_is_rejected():
    assert is_valid_date("2025-13-99") is False


def test_a_date_with_a_time_is_rejected():
    assert is_valid_date("2025-01-01 12:00:00") is False
