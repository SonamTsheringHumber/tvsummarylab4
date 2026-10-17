import pytest

from tvsummary.aggregations import (
    Aggregation,
    AverageRatingByLanguage,
    MissingValues,
    ShowsPerDecade,
    ShowsPerGenre,
    TopRatedShows,
    default_aggregations,
)


def test_shows_per_genre_orders_by_count_then_name(shows):
    result = ShowsPerGenre().compute(shows)
    assert list(result.items()) == [("Drama", 2), ("Comedy", 1), ("Crime", 1)]


def test_average_rating_by_language_skips_unrated_shows(shows):
    assert AverageRatingByLanguage().compute(shows) == {
        "English": {"average_rating": 7.0, "rated_shows": 2},
        "unknown": {"average_rating": 9.0, "rated_shows": 1},
    }


def test_shows_per_decade_skips_missing_dates(shows):
    assert ShowsPerDecade().compute(shows) == {"1990s": 1, "2000s": 1, "2010s": 1}


def test_top_rated_shows_respects_n(shows):
    assert TopRatedShows(n=2).compute(shows) == [
        {"name": "Delta", "rating": 9.0},
        {"name": "Alpha", "rating": 8.0},
    ]


def test_missing_values_counts_each_field(shows):
    assert MissingValues().compute(shows) == {
        "no_genre": 1,
        "no_rating": 1,
        "no_language": 1,
        "no_premiere_date": 1,
        "no_network_or_web_channel": 2,
    }


def test_base_class_must_be_overridden():
    with pytest.raises(NotImplementedError, match="override"):
        Aggregation().compute([])


def test_default_aggregations_have_unique_names():
    names = [aggregation.name for aggregation in default_aggregations()]
    assert len(names) == len(set(names)) == 5
