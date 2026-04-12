# ruff: noqa: E501, PLR2004
import pytest

from scrapers.parsers.infobox.text_utils.circuit.specs import CircuitSpecsParser


@pytest.fixture()
def parser() -> CircuitSpecsParser:
    return CircuitSpecsParser()


# ---------------------------------------------------------------------------
# _norm_surface_part  (lines 25, 28)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("surface_part", "expected_contains"),
    [
        ("asphalt", "Asphalt"),
        ("tarmac", "Asphalt"),
        ("concrete", "Concrete"),
        ("asphalt concrete", "Asphalt"),  # asphalt beats concrete
        ("cobblestones", "Cobblestones"),
        ("brick", "Brick"),
        ("dirt track", "Dirt"),
        ("wood planks", "Wood"),
        ("unknown material", "unknown material"),  # no match → raw text returned
    ],
)
def test_norm_surface_part(surface_part, expected_contains) -> None:
    result = CircuitSpecsParser._norm_surface_part(surface_part)
    assert expected_contains in result


def test_norm_surface_part_unique() -> None:
    # duplicates should not appear
    result = CircuitSpecsParser._norm_surface_part("asphalt and asphalt")
    assert result.count("Asphalt") == 1


# ---------------------------------------------------------------------------
# parse_surface  (lines 43, 64, 78-100)
# ---------------------------------------------------------------------------


def test_parse_surface_none() -> None:
    assert CircuitSpecsParser.parse_surface(None) is None


def test_parse_surface_empty_text() -> None:
    assert CircuitSpecsParser.parse_surface({"text": ""}) is None


def test_parse_surface_single() -> None:
    result = CircuitSpecsParser.parse_surface({"text": "Asphalt"})
    assert result is not None
    assert "Asphalt" in result["values"]


def test_parse_surface_with_and() -> None:
    # line 64: "and" treated as separator
    result = CircuitSpecsParser.parse_surface({"text": "Asphalt and Concrete"})
    assert result is not None
    assert "Asphalt" in result["values"]
    assert "Concrete" in result["values"]


def test_parse_surface_with_ampersand() -> None:
    result = CircuitSpecsParser.parse_surface({"text": "Asphalt & Brick"})
    assert result is not None
    assert "Asphalt" in result["values"]
    assert "Brick" in result["values"]


def test_parse_surface_with_slash() -> None:
    result = CircuitSpecsParser.parse_surface({"text": "Asphalt/Concrete"})
    assert result is not None


def test_parse_surface_with_note() -> None:
    result = CircuitSpecsParser.parse_surface(
        {"text": "Asphalt (partially repaved 2018)"},
    )
    assert result is not None
    assert result.get("note") == "partially repaved 2018"


def test_parse_surface_no_known_material() -> None:
    result = CircuitSpecsParser.parse_surface({"text": "Gravel"})
    assert result is not None
    # falls back to raw text
    assert result["values"] == ["Gravel"]


def test_parse_surface_only_unknown_stripped() -> None:
    result = CircuitSpecsParser.parse_surface({"text": "  . "})
    assert result is None


# ---------------------------------------------------------------------------
# _parse_capacity  (lines 78-100)
# ---------------------------------------------------------------------------


def test_parse_capacity_none() -> None:
    assert CircuitSpecsParser._parse_capacity(None) is None


def test_parse_capacity_empty() -> None:
    assert CircuitSpecsParser._parse_capacity({"text": ""}) is None


def test_parse_capacity_total_only() -> None:
    result = CircuitSpecsParser._parse_capacity({"text": "125,000"})
    assert result is not None
    assert result["total"] == 125000


def test_parse_capacity_with_seating() -> None:
    result = CircuitSpecsParser._parse_capacity({"text": "125,000 (44,000 seating)"})
    assert result is not None
    assert result["total"] == 125000
    assert result["seating"] == 44000


def test_parse_capacity_with_ref() -> None:
    result = CircuitSpecsParser._parse_capacity({"text": "50000[1]"})
    assert result is not None
    assert result["total"] == 50000


def test_parse_capacity_no_numbers() -> None:
    assert CircuitSpecsParser._parse_capacity({"text": "unknown"}) is None


# ---------------------------------------------------------------------------
# _extract_currency  (lines 104-108)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("€10 million", "EUR"),
        ("$250 million", "USD"),
        ("£50m", "GBP"),
        ("¥1 billion", "JPY"),
        ("EUR 10 million", "EUR"),
        ("USD 250 million", "USD"),
        ("no currency here", None),
    ],
)
def test_extract_currency(text, expected) -> None:
    assert CircuitSpecsParser._extract_currency(text) == expected


# ---------------------------------------------------------------------------
# _parse_construction_cost  (lines 115-150)
# ---------------------------------------------------------------------------


def test_parse_construction_cost_none(parser) -> None:
    assert parser._parse_construction_cost(None) is None


def test_parse_construction_cost_empty(parser) -> None:
    assert parser._parse_construction_cost({"text": ""}) is None


def test_parse_construction_cost_basic(parser) -> None:
    result = parser._parse_construction_cost({"text": "$250 million"})
    assert result is not None
    assert result["currency"] == "USD"
    assert result["amount"] == pytest.approx(250.0)
    assert result["scale"] == "million"


def test_parse_construction_cost_billion(parser) -> None:
    result = parser._parse_construction_cost({"text": "€1.5 billion"})
    assert result is not None
    assert result["scale"] == "billion"


def test_parse_construction_cost_no_amount_no_currency(parser) -> None:
    assert parser._parse_construction_cost({"text": "not a cost"}) is None


def test_parse_construction_cost_no_scale(parser) -> None:
    result = parser._parse_construction_cost({"text": "$500"})
    assert result is not None
    assert "scale" not in result


# ---------------------------------------------------------------------------
# parse_banking  (lines 159, 175)
# ---------------------------------------------------------------------------


def test_parse_banking_none() -> None:
    assert CircuitSpecsParser.parse_banking(None) is None


def test_parse_banking_empty() -> None:
    assert CircuitSpecsParser.parse_banking({"text": ""}) is None


def test_parse_banking_degrees() -> None:
    result = CircuitSpecsParser.parse_banking({"text": "33°"})
    assert result is not None
    assert result["value"] == pytest.approx(33.0)
    assert result["unit"] == "deg"


def test_parse_banking_percent() -> None:
    result = CircuitSpecsParser.parse_banking({"text": "12%"})
    assert result is not None
    assert result["value"] == pytest.approx(12.0)
    assert result["unit"] == "percent"


def test_parse_banking_with_note() -> None:
    result = CircuitSpecsParser.parse_banking({"text": "33° (banked turn 1)"})
    assert result is not None
    assert result.get("note") is not None


def test_parse_banking_no_value() -> None:
    result = CircuitSpecsParser.parse_banking({"text": "steeply banked"})
    assert result is not None
    assert "value" not in result
    assert result.get("note") == "steeply banked"

