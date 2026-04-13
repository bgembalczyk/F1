from bs4 import BeautifulSoup

from scrapers.extractors.numeric_extractor import NumericExtractor


def cell(text: str):
    return BeautifulSoup(f"<td>{text}</td>", "html.parser").find("td")


def test_parse_int_cell_numeric_vs_text() -> None:
    assert NumericExtractor.parse_int_cell(cell("1,234 entries")) == 1234  # noqa: PLR2004
    assert NumericExtractor.parse_int_cell(cell("unknown")) is None


def test_parse_float_cell_numeric_vs_text() -> None:
    assert NumericExtractor.parse_float_cell(cell("3.14 litre")) == 3.14  # noqa: PLR2004
    assert NumericExtractor.parse_float_cell(cell("n/a")) is None


def test_parse_entries_with_missing_start_value() -> None:
    assert NumericExtractor.parse_entries(cell("120 (95)")) == {
        "entries": 120,
        "starts": 95,
    }
    assert NumericExtractor.parse_entries(cell("120")) == {
        "entries": 120,
        "starts": None,
    }
