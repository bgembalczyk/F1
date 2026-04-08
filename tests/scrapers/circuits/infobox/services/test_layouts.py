# ruff: noqa: E501, PLR2004
from typing import Any
from unittest.mock import MagicMock

import pytest
from bs4 import BeautifulSoup

from scrapers.circuits.infobox.services.lap_record import CircuitLapRecordParser
from scrapers.circuits.infobox.services.layouts import CircuitLayoutsParser
from scrapers.circuits.infobox.services.specs import CircuitSpecsParser
from scrapers.circuits.infobox.services.text_utils import InfoboxTextUtils


def make_parser() -> CircuitLayoutsParser:
    infobox_scraper = MagicMock()
    text_utils = InfoboxTextUtils()
    lap_record_parser = CircuitLapRecordParser()
    specs_parser = CircuitSpecsParser()
    return CircuitLayoutsParser(
        infobox_scraper=infobox_scraper,
        text_utils=text_utils,
        lap_record_parser=lap_record_parser,
        specs_parser=specs_parser,
    )


@pytest.fixture()
def parser() -> CircuitLayoutsParser:
    return make_parser()


# ---------------------------------------------------------------------------
# _is_layout_header  (lines 66-67 area)
# ---------------------------------------------------------------------------


def test_is_layout_header_true() -> None:
    html = '<th class="infobox-header" colspan="2">Layout 1</th>'
    tag = BeautifulSoup(html, "html.parser").find("th")
    assert CircuitLayoutsParser._is_layout_header(tag) is True


def test_is_layout_header_no_colspan() -> None:
    html = '<th class="infobox-header">Layout 1</th>'
    tag = BeautifulSoup(html, "html.parser").find("th")
    assert CircuitLayoutsParser._is_layout_header(tag) is False


def test_is_layout_header_no_class() -> None:
    html = '<th colspan="2">Layout 1</th>'
    tag = BeautifulSoup(html, "html.parser").find("th")
    assert CircuitLayoutsParser._is_layout_header(tag) is False


# ---------------------------------------------------------------------------
# _apply_layout_field  (lines 66-81)
# ---------------------------------------------------------------------------


def test_apply_layout_field_length(parser) -> None:
    current: dict[str, Any] = {}
    cell_row = {"text": "5.793 km", "links": []}
    parser._apply_layout_field(current, "length", cell_row)
    assert "length_km" in current
    assert "length_mi" in current


def test_apply_layout_field_turns(parser) -> None:
    current: dict[str, Any] = {}
    cell_row = {"text": "17", "links": []}
    parser._apply_layout_field(current, "turns", cell_row)
    assert current.get("turns") == 17


def test_apply_layout_field_race_lap_record(parser) -> None:
    current: dict[str, Any] = {}
    cell_row = {"text": "1:23.456 (Hamilton, Ferrari, 2019)", "links": []}
    parser._apply_layout_field(current, "race_lap_record", cell_row)
    assert "race_lap_record" in current


def test_apply_layout_field_surface(parser) -> None:
    current: dict[str, Any] = {}
    cell_row = {"text": "Asphalt", "links": []}
    parser._apply_layout_field(current, "surface", cell_row)
    assert "surface" in current


def test_apply_layout_field_banking(parser) -> None:
    current: dict[str, Any] = {}
    cell_row = {"text": "33°", "links": []}
    parser._apply_layout_field(current, "banking", cell_row)
    assert "banking" in current


def test_apply_layout_field_unknown_label(parser) -> None:
    # unknown label → no-op, current unchanged
    current: dict[str, Any] = {}
    cell_row = {"text": "something", "links": []}
    parser._apply_layout_field(current, "unknown_field", cell_row)
    assert current == {}


# ---------------------------------------------------------------------------
# parse_layout_sections  (line 96 - table is None)
# ---------------------------------------------------------------------------


def test_parse_layout_sections_no_table(parser) -> None:
    parser.infobox_scraper.parser.find_infobox.return_value = None
    soup = BeautifulSoup("<html></html>", "html.parser")
    assert parser.parse_layout_sections(soup) == []


# ---------------------------------------------------------------------------
# _parse_layout_header  (line 119, 134)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected_name", "expected_years"),
    [
        ("Layout A (1990-2005)", "Layout A", "1990-2005"),
        ("Layout B", "Layout B", None),
        ("No years here", "No years here", None),
    ],
)
def test_parse_layout_header(text, expected_name, expected_years) -> None:
    name, years = CircuitLayoutsParser._parse_layout_header(text)
    assert name == expected_name
    assert years == expected_years
