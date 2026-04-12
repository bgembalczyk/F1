# ruff: noqa: E501, PLR2004
import pytest

from scrapers.parsers.infobox.text_utils.circuit.geo import CircuitGeoParser


@pytest.fixture()
def parser() -> CircuitGeoParser:
    return CircuitGeoParser()


# ---------------------------------------------------------------------------
# _split_plain_segment  (line 40 - stopword filtering)
# ---------------------------------------------------------------------------


def test_split_plain_segment_basic() -> None:
    result = CircuitGeoParser._split_plain_segment("Italy, Rome")
    assert "Italy" in result
    assert "Rome" in result


def test_split_plain_segment_stopwords_removed() -> None:
    result = CircuitGeoParser._split_plain_segment("Italy and France")
    assert "and" not in result
    assert "&" not in result


def test_split_plain_segment_empty() -> None:
    assert CircuitGeoParser._split_plain_segment("") == []


# ---------------------------------------------------------------------------
# _components_from_links  (line 44 - processing links)
# ---------------------------------------------------------------------------


def test_components_from_links_with_links(parser) -> None:
    links = [{"text": "Italy", "url": "https://en.wikipedia.org/wiki/Italy"}]
    components = parser._components_from_links("Rome, Italy", links)
    texts = [c["text"] for c in components]
    assert "Italy" in texts
    link_comp = next(c for c in components if c["text"] == "Italy")
    assert "link" in link_comp


def test_components_from_links_no_links(parser) -> None:
    components = parser._components_from_links("Rome, Italy", [])
    texts = [c["text"] for c in components]
    assert "Rome" in texts
    assert "Italy" in texts


def test_components_from_links_link_not_in_text(parser) -> None:
    links = [{"text": "France", "url": "https://en.wikipedia.org/wiki/France"}]
    components = parser._components_from_links("Italy, Rome", links)
    assert all(c.get("link") is None for c in components)


# ---------------------------------------------------------------------------
# parse_location  (line 84 - returns None when no components)
# ---------------------------------------------------------------------------


def test_parse_location_none(parser) -> None:
    assert parser.parse_location(None) is None


def test_parse_location_empty_text(parser) -> None:
    assert parser.parse_location({"text": ""}) is None


def test_parse_location_only_stopwords(parser) -> None:
    # Pure stopwords are filtered out - empty text returns None
    result = parser.parse_location({"text": "", "links": []})
    assert result is None


def test_parse_location_valid(parser) -> None:
    result = parser.parse_location({"text": "Monza, Italy", "links": []})
    assert result is not None
    assert "localisation1" in result


# ---------------------------------------------------------------------------
# parse_coordinates  (line 114 - None row)
# ---------------------------------------------------------------------------


def test_parse_coordinates_none(parser) -> None:
    assert parser.parse_coordinates(None) is None


def test_parse_coordinates_empty_text(parser) -> None:
    assert parser.parse_coordinates({"text": ""}) is None


# ---------------------------------------------------------------------------
# _parse_position_payload  (lines 130-142 - directional coords)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected_lat", "expected_lon"),
    [
        ("45.5; 9.2", 45.5, 9.2),
        ("-33.8; 151.2", -33.8, 151.2),
        ("N45 E9", 45.0, 9.0),
        ("S45 W9", -45.0, -9.0),
        ("S33.8 E151.2", -33.8, 151.2),
    ],
)
def test_parse_position_payload(text, expected_lat, expected_lon) -> None:
    result = CircuitGeoParser._parse_position_payload(text)
    assert result is not None
    assert result["lat"] == pytest.approx(expected_lat, rel=1e-4)
    assert result["lon"] == pytest.approx(expected_lon, rel=1e-4)


def test_parse_position_payload_empty() -> None:
    assert CircuitGeoParser._parse_position_payload("") is None


def test_parse_position_payload_no_coords() -> None:
    assert CircuitGeoParser._parse_position_payload("no coords here") is None


# ---------------------------------------------------------------------------
# _parse_area  (lines 147-171)
# ---------------------------------------------------------------------------


def test_parse_area_none() -> None:
    assert CircuitGeoParser._parse_area(None) is None


def test_parse_area_empty_text() -> None:
    assert CircuitGeoParser._parse_area({"text": ""}) is None


def test_parse_area_acres_and_ha() -> None:
    result = CircuitGeoParser._parse_area({"text": "277 acres (112 ha)"})
    assert result is not None
    assert result["acres"] == pytest.approx(277.0)
    assert result["hectares"] == pytest.approx(112.0)


def test_parse_area_only_ha() -> None:
    result = CircuitGeoParser._parse_area({"text": "112 ha"})
    assert result is not None
    assert result["hectares"] == pytest.approx(112.0)
    assert "acres" not in result


def test_parse_area_only_acres() -> None:
    result = CircuitGeoParser._parse_area({"text": "277 acres"})
    assert result is not None
    assert result["acres"] == pytest.approx(277.0)


def test_parse_area_no_units_returns_none() -> None:
    assert CircuitGeoParser._parse_area({"text": "no area here"}) is None


# ---------------------------------------------------------------------------
# _filter_components
# ---------------------------------------------------------------------------


def test_filter_components_removes_stopwords() -> None:
    comps = [{"text": "and"}, {"text": "Italy"}]
    result = CircuitGeoParser._filter_components(comps)
    assert len(result) == 1
    assert result[0]["text"] == "Italy"


def test_filter_components_removes_empty() -> None:
    comps = [{"text": ""}, {"text": "Italy"}]
    result = CircuitGeoParser._filter_components(comps)
    assert len(result) == 1
