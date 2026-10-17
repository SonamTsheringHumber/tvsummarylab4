import pytest

from tvsummary.models import Show


def test_missing_genre_list_gives_empty_set():
    assert Show({"id": 1, "name": "X"}).genres == set()


def test_missing_rating_gives_none():
    assert Show({"id": 1, "name": "X"}).rating is None
    assert Show({"id": 1, "name": "X", "rating": {"average": None}}).rating is None


@pytest.mark.parametrize(
    ("rating", "expected"),
    [
        ({"average": 7.5}, 7.5),
        ({"average": 0}, 0.0),
        ({"average": 11}, None),
        ({"average": True}, None),
        ({"average": "8"}, None),
        ("8.0", None),
        (None, None),
    ],
)
def test_rating_cleaning(rating, expected):
    assert Show({"id": 1, "name": "X", "rating": rating}).rating == expected


@pytest.mark.parametrize(
    ("premiered", "expected"),
    [
        ("1999-05-05", 1999),
        ("2020", 2020),
        ("abcd-01-01", None),
        ("1700-01-01", None),
        (None, None),
    ],
)
def test_premiere_year_cleaning(premiered, expected):
    show = Show({"id": 1, "name": "X", "premiered": premiered})
    assert show.premiere_year == expected


@pytest.mark.parametrize(
    ("language", "expected"),
    [(" English ", "English"), ("   ", None), (None, None), (5, None)],
)
def test_language_cleaning(language, expected):
    assert Show({"id": 1, "name": "X", "language": language}).language == expected


def test_genres_are_stripped_and_junk_dropped():
    show = Show({"id": 1, "name": "X", "genres": ["Drama", " ", 5, " Comedy "]})
    assert show.genres == {"Drama", "Comedy"}


def test_str_shows_name_and_rating():
    show = Show({"id": 1, "name": "X", "rating": {"average": 8}})
    assert str(show) == "X (rating: 8.0)"
