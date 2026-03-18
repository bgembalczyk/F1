"""Focused tests for `to` year-range parsing in season service."""

from models.services import parse_seasons


def test_season_service_to_range() -> None:
    """'1997 to 1999' is parsed as a full year range."""

    result = parse_seasons("1997 to 1999")
    years = [e["year"] for e in result]
    assert years == [1997, 1998, 1999]


def test_season_service_to_range_mixed_with_comma() -> None:
    """'1997 to 1999, 2001' is parsed correctly."""

    result = parse_seasons("1997 to 1999, 2001")
    years = [e["year"] for e in result]
    assert years == [1997, 1998, 1999, 2001]


def test_season_service_to_range_case_insensitive() -> None:
    """'1997 TO 1999' (uppercase) is also parsed correctly."""

    result = parse_seasons("1997 TO 1999")
    years = [e["year"] for e in result]
    assert years == [1997, 1998, 1999]
