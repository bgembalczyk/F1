from bs4 import BeautifulSoup

from scrapers.drivers.infobox.parsers.numeric import NumericParser


def cell(text: str):
    return BeautifulSoup(f"<td>{text}</td>", "html.parser").find("td")


def test_parse_int_cell_numeric_vs_text() -> None:
    assert NumericParser.parse_int_cell(cell("1,234 entries")) == 1234  # noqa: PLR2004
    assert NumericParser.parse_int_cell(cell("unknown")) is None


def test_parse_float_cell_numeric_vs_text() -> None:
    assert NumericParser.parse_float_cell(cell("3.14 litre")) == 3.14  # noqa: PLR2004
    assert NumericParser.parse_float_cell(cell("n/a")) is None


def test_parse_entries_with_missing_start_value() -> None:
    assert NumericParser.parse_entries(cell("120 (95)")) == {
        "entries": 120,
        "starts": 95,
    }
    assert NumericParser.parse_entries(cell("120")) == {"entries": 120, "starts": None}
