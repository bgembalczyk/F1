# ruff: noqa: E501, PLR2004
import pytest

from scrapers.circuits.circuits_infobox.services.entity_parsing import (
    CircuitEntityParser,
)


@pytest.fixture()
def parser() -> CircuitEntityParser:
    return CircuitEntityParser()


# ---------------------------------------------------------------------------
# _split_entity_parts  (line 15 - empty string)
# ---------------------------------------------------------------------------


def test_split_entity_parts_empty(parser) -> None:
    assert parser._split_entity_parts("") == []


def test_split_entity_parts_single(parser) -> None:
    assert parser._split_entity_parts("Monza") == ["Monza"]


def test_split_entity_parts_multiple(parser) -> None:
    result = parser._split_entity_parts("Alpha, Beta and Gamma")
    assert len(result) == 3


# ---------------------------------------------------------------------------
# _links_to_entities  (line 54)
# ---------------------------------------------------------------------------


def test_links_to_entities_valid(parser) -> None:
    links = [
        {"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"},
        {"text": "Spa", "url": "https://en.wikipedia.org/wiki/Spa"},
    ]
    result = parser._links_to_entities(links)
    assert len(result) == 2
    assert result[0]["text"] == "Monza"


def test_links_to_entities_empty(parser) -> None:
    assert parser._links_to_entities([]) == []


def test_links_to_entities_filters_invalid(parser) -> None:
    links = [{"text": "", "url": None}]
    result = parser._links_to_entities(links)
    assert result == []


# ---------------------------------------------------------------------------
# _parts_to_entities  (lines 66-67, 71-73 - with/without match)
# ---------------------------------------------------------------------------


def test_parts_to_entities_with_matching_link(parser) -> None:
    parts = ["Monza"]
    links = [{"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}]
    result = parser._parts_to_entities(parts, links)
    assert result[0]["text"] == "Monza"
    assert result[0]["url"] == "https://en.wikipedia.org/wiki/Monza"


def test_parts_to_entities_without_matching_link(parser) -> None:
    parts = ["Monza", "Spa"]
    links = [{"text": "Unknown", "url": "https://en.wikipedia.org/wiki/Unknown"}]
    result = parser._parts_to_entities(parts, links)
    assert result[0] == {"text": "Monza", "url": None}
    assert result[1] == {"text": "Spa", "url": None}


# ---------------------------------------------------------------------------
# _build_from_multiple_links  (line 90 - fallback when entities empty)
# ---------------------------------------------------------------------------


def test_build_from_multiple_links_with_valid_links(parser) -> None:
    parts = ["Monza", "Spa"]
    links = [
        {"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"},
        {"text": "Spa", "url": "https://en.wikipedia.org/wiki/Spa"},
    ]
    result = parser._build_from_multiple_links(parts, links)
    assert isinstance(result, list)
    assert len(result) == 2


def test_build_from_multiple_links_empty_links_fallback(parser) -> None:
    # links with empty/invalid entries → fallback to stripped string
    parts = ["Alpha", "Beta"]
    links = [{"text": "", "url": None}, {"text": "", "url": None}]
    result = parser._build_from_multiple_links(parts, links)
    assert isinstance(result, str)
    assert "Alpha" in result


# ---------------------------------------------------------------------------
# _build_without_links  (line 101 - single part)
# ---------------------------------------------------------------------------


def test_build_without_links_single_part() -> None:
    result = CircuitEntityParser._build_without_links(["Monza"])
    assert result == "Monza"


def test_build_without_links_multiple_parts() -> None:
    result = CircuitEntityParser._build_without_links(["Monza", "Spa"])
    assert isinstance(result, list)
    assert len(result) == 2


def test_build_without_links_empty() -> None:
    assert CircuitEntityParser._build_without_links([]) is None


# ---------------------------------------------------------------------------
# _build_from_single_link  (lines 109-115)
# ---------------------------------------------------------------------------


def test_build_from_single_link_single_part_with_url(parser) -> None:
    link = {"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}
    result = parser._build_from_single_link(["Monza"], link)
    assert isinstance(result, dict)
    assert result["text"] == "Monza"
    assert result["url"] == "https://en.wikipedia.org/wiki/Monza"


def test_build_from_single_link_multiple_parts(parser) -> None:
    link = {"text": "Alpha", "url": "https://en.wikipedia.org/wiki/Alpha"}
    result = parser._build_from_single_link(["Alpha", "Beta"], link)
    assert isinstance(result, list)
    assert len(result) == 2


def test_build_from_single_link_empty_parts(parser) -> None:
    link = {"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}
    result = parser._build_from_single_link([], link)
    # clean_link_record should produce a dict with no text override
    assert result is not None


def test_build_from_single_link_invalid_link_no_parts(parser) -> None:
    link = {"text": "", "url": None}
    result = parser._build_from_single_link([], link)
    assert result is None


# ---------------------------------------------------------------------------
# linked entity parsing (integration)
# ---------------------------------------------------------------------------


def test_parse_linked_entity_none(parser) -> None:
    assert parser.parse_linked_entity(None) is None


def test_parse_linked_entity_empty_text(parser) -> None:
    assert parser.parse_linked_entity({"text": ""}) is None


def test_parse_linked_entity_plain_text(parser) -> None:
    result = parser.parse_linked_entity({"text": "Monza", "links": []})
    assert result == "Monza"


def test_parse_linked_entity_with_link(parser) -> None:
    links = [{"text": "Monza", "url": "https://en.wikipedia.org/wiki/Monza"}]
    result = parser.parse_linked_entity({"text": "Monza", "links": links})
    assert isinstance(result, dict)
    assert result["text"] == "Monza"


# ---------------------------------------------------------------------------
# _parse_website
# ---------------------------------------------------------------------------


def test_parse_website_none() -> None:
    assert CircuitEntityParser._parse_website(None) is None


def test_parse_website_text_only() -> None:
    result = CircuitEntityParser._parse_website({"text": "www.monza.it", "links": []})
    assert result == "www.monza.it"


def test_parse_website_with_link() -> None:
    links = [{"text": "Website", "url": "https://www.monza.it"}]
    result = CircuitEntityParser._parse_website({"text": "Website", "links": links})
    assert result == "https://www.monza.it"
