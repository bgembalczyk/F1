# ruff: noqa: E501, PLR2004
import pytest

from scrapers.parsers.infobox.text_utils.circuit import CircuitAdditionalInfoExtractor


@pytest.fixture()
def parser() -> CircuitAdditionalInfoExtractor:
    return CircuitAdditionalInfoExtractor()


# ---------------------------------------------------------------------------
# collect_additional_info  (lines 28, 35-42, 45)
# ---------------------------------------------------------------------------


def test_collect_additional_info_skips_used_keys(parser) -> None:
    rows = {
        "location": {"text": "Monza, Italy", "links": []},
        "extra": {"text": "Some value", "links": []},
    }
    used = {"location"}
    result = parser.collect_additional_info(rows, used)
    assert result is not None
    assert "location" not in result
    assert "extra" in result


def test_collect_additional_info_skips_empty_text(parser) -> None:
    rows = {
        "key1": {"text": "", "links": []},
        "key2": {"text": "  ", "links": []},
    }
    result = parser.collect_additional_info(rows, set())
    assert result is None


def test_collect_additional_info_multiple_parts(parser) -> None:
    # multiple comma-separated parts → values list
    rows = {
        "sponsors": {"text": "Alpha, Beta, Gamma", "links": []},
    }
    result = parser.collect_additional_info(rows, set())
    assert result is not None
    entry = result["sponsors"]
    assert "values" in entry
    assert len(entry["values"]) == 3


def test_collect_additional_info_multiple_parts_with_link(parser) -> None:
    links = [{"text": "Alpha", "url": "https://en.wikipedia.org/wiki/Alpha"}]
    rows = {
        "sponsors": {"text": "Alpha, Beta", "links": links},
    }
    result = parser.collect_additional_info(rows, set())
    assert result is not None
    entry = result["sponsors"]
    assert "values" in entry
    # Alpha should be a dict with url
    alpha = next(
        (
            v
            for v in entry["values"]
            if isinstance(v, dict) and v.get("text") == "Alpha"
        ),
        None,
    )
    assert alpha is not None
    assert alpha["url"] == "https://en.wikipedia.org/wiki/Alpha"


def test_collect_additional_info_single_value_with_links(parser) -> None:
    # single value but with links → info should contain links key
    links = [{"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}]
    rows = {
        "circuit": {"text": "Monza", "links": links},
    }
    result = parser.collect_additional_info(rows, set())
    assert result is not None
    entry = result["circuit"]
    assert "links" in entry


def test_collect_additional_info_all_used(parser) -> None:
    rows = {"location": {"text": "Rome", "links": []}}
    result = parser.collect_additional_info(rows, {"location"})
    assert result is None


def test_collect_additional_info_empty_rows(parser) -> None:
    result = parser.collect_additional_info({}, set())
    assert result is None
