import pytest

from models.value_objects import Link, SeasonRef


def test_link_strips_text_and_keeps_url():
    link = Link(text="  Example  ", url="https://example.com")

    assert link.text == "Example"
    assert link.url == "https://example.com"
    assert link.to_dict() == {"text": "Example", "url": "https://example.com"}


def test_link_rejects_invalid_url():
    with pytest.raises(ValueError, match="nieprawidłowy URL"):
        Link(text="Example", url="notaurl")


def test_link_is_empty_checks_both_fields():
    assert Link().is_empty() is True
    assert Link(text="Example").is_empty() is False
    assert Link(url="https://example.com").is_empty() is False


def test_link_from_dict_handles_none_payload():
    link = Link.from_dict(None)

    assert link == Link()


def test_season_ref_coerces_year_and_validates_url():
    season = SeasonRef(year="2020", url="https://example.com/2020")

    assert season.year == 2020
    assert season.to_dict() == {"year": 2020, "url": "https://example.com/2020"}


def test_season_ref_rejects_invalid_url():
    with pytest.raises(ValueError, match="nieprawidłowy URL"):
        SeasonRef(year=2020, url="notaurl")


def test_season_ref_rejects_negative_year():
    with pytest.raises(ValueError, match="year nie może być ujemne"):
        SeasonRef(year=-1)


def test_season_ref_from_dict_requires_year():
    assert SeasonRef.from_dict({"url": "https://example.com"}) is None
