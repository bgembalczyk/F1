# ruff: noqa: E501, PLR2004
import pytest

from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils


@pytest.fixture()
def utils() -> InfoboxTextUtils:
    return InfoboxTextUtils()


# ---------------------------------------------------------------------------
# _split_simple_list  (lines 27-31)
# ---------------------------------------------------------------------------


def test_split_simple_list_none_row(utils) -> None:
    assert utils._split_simple_list(None) is None


def test_split_simple_list_empty_text(utils) -> None:
    assert utils._split_simple_list({"text": ""}) is None


def test_split_simple_list_single(utils) -> None:
    result = utils._split_simple_list({"text": "Monza"})
    assert result == ["Monza"]


def test_split_simple_list_multiple(utils) -> None:
    result = utils._split_simple_list({"text": "Monza, Spa, Silverstone"})
    assert result is not None
    assert len(result) == 3


# ---------------------------------------------------------------------------
# parse_int  (lines ~34-41)
# ---------------------------------------------------------------------------


def test_parse_int_none(utils) -> None:
    assert utils.parse_int(None) is None


def test_parse_int_valid(utils) -> None:
    assert utils.parse_int({"text": "17"}) == 17


def test_parse_int_invalid(utils) -> None:
    # should not raise, returns None on parse error
    result = utils.parse_int({"text": "not-a-number"})
    assert result is None


# ---------------------------------------------------------------------------
# parse_length  (lines ~44-53)
# ---------------------------------------------------------------------------


def test_parse_length_none(utils) -> None:
    assert utils.parse_length(None, unit="km") is None


def test_parse_length_valid_km(utils) -> None:
    result = utils.parse_length({"text": "5.793 km"}, unit="km")
    assert result == pytest.approx(5.793, rel=1e-3)


def test_parse_length_valid_mi(utils) -> None:
    result = utils.parse_length({"text": "3.600 mi"}, unit="mi")
    assert result == pytest.approx(3.6, rel=1e-3)


# ---------------------------------------------------------------------------
# _parse_dates  (lines ~56-76 / line 64, 72, 76)
# ---------------------------------------------------------------------------


def test_parse_dates_none(utils) -> None:
    assert utils._parse_dates(None) is None


def test_parse_dates_empty_text(utils) -> None:
    # row present but text empty after clean
    assert utils._parse_dates({"text": ""}) is None


def test_parse_dates_year_only(utils) -> None:
    result = utils._parse_dates({"text": "1985"})
    assert result is not None
    assert result["years"] == ["1985"]


def test_parse_dates_full_date(utils) -> None:
    result = utils._parse_dates({"text": "15 March 2001"})
    assert result is not None
    assert result["iso_dates"] is not None


# ---------------------------------------------------------------------------
# _find_link  (line 100)
# ---------------------------------------------------------------------------


def test_find_link_empty_text(utils) -> None:
    links = [{"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}]
    assert utils._find_link(None, links) is None
    assert utils._find_link("", links) is None


def test_find_link_match(utils) -> None:
    links = [{"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}]
    result = utils._find_link("Monza", links)
    assert result is not None
    assert result["url"] == "https://en.wikipedia.org/wiki/Monza"


def test_find_link_no_match(utils) -> None:
    links = [{"text": "Spa", "url": "https://en.wikipedia.org/wiki/Spa"}]
    assert utils._find_link("Monza", links) is None


# ---------------------------------------------------------------------------
# _with_link  (lines 113-124)
# ---------------------------------------------------------------------------


def test_with_link_none_text(utils) -> None:
    assert utils._with_link(None, []) is None


def test_with_link_no_links(utils) -> None:
    result = utils._with_link("Monza", [])
    assert result == {"text": "Monza", "url": None}


def test_with_link_with_valid_link(utils) -> None:
    links = [{"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}]
    result = utils._with_link("Monza", links)
    assert result == {"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}


def test_with_link_redlink_ignored(utils) -> None:
    # Wikipedia redlink pattern (w/index.php?title=...)
    links = [
        {
            "text": "Stub",
            "url": "https://en.wikipedia.org/w/index.php?title=Stub&action=edit&redlink=1",
        },
    ]
    result = utils._with_link("Stub", links)
    assert result is not None
    assert result["url"] is None


def test_with_link_none_links_arg(utils) -> None:
    result = utils._with_link("text", None)
    assert result == {"text": "text", "url": None}


# ---------------------------------------------------------------------------
# prune_nulls
# ---------------------------------------------------------------------------


def test_prune_nulls(utils) -> None:
    data = {"a": None, "b": 1, "c": {}, "d": []}
    result = utils.prune_nulls(data)
    assert result == {"b": 1}
