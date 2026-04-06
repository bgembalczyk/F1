# ruff: noqa: SLF001

import pytest
from bs4 import BeautifulSoup

from scrapers.engines.engine_restrictions import EngineRestrictionsScraper
from scrapers.engines.engine_restrictions import EngineSubSectionParser


def test_engine_restrictions_apply_for_elements_covers_all_guards() -> None:
    parser = EngineSubSectionParser()

    class _TableParserStub:
        def parse(self, data):
            return {"parsed": True} if data.get("ok") else None

    parser._table_parser = _TableParserStub()
    elements = [
        {"kind": "text", "data": {"ok": True}},
        {"kind": "table", "data": []},
        {"kind": "table", "data": {"ok": False}},
        {"kind": "table", "data": {"ok": True}},
    ]

    parser._apply_for_elements(elements)

    assert elements[0]["data"] == {"ok": True}
    assert elements[1]["data"] == []
    assert elements[2]["data"] == {"ok": False}
    assert elements[3]["data"] == {"parsed": True}


def test_engine_restrictions_parse_soup_raises_for_missing_header_or_incomplete() -> None:
    scraper = EngineRestrictionsScraper()

    with pytest.raises(RuntimeError, match="wiersza nagłówkowego"):
        soup = BeautifulSoup("<table></table>", "html.parser")
        scraper._find_table = lambda _soup: _soup.find("table")
        scraper._parse_soup(soup)

    with pytest.raises(RuntimeError, match="niekompletny"):
        soup = BeautifulSoup("<table><tr><th>Year</th></tr></table>", "html.parser")
        scraper._find_table = lambda _soup: _soup.find("table")
        scraper._parse_soup(soup)


def test_engine_restrictions_parse_soup_transposes_rows_and_fills_missing_cells() -> None:
    scraper = EngineRestrictionsScraper()
    soup = BeautifulSoup(
        """
        <h2><span id="Engine">Engine</span></h2>
        <table class="wikitable">
          <tr><th>Year</th><th>2000-2005</th><th>2006-2013</th><th>2014-2025</th></tr>
          <tr><th>Size</th><td>3.0 L</td><td>2.4 L</td><td>1.6 L</td></tr>
          <tr><th>Type of engine</th><td>V10</td><td>V8</td></tr>
        </table>
        """,
        "html.parser",
    )

    records = scraper._parse_soup(soup)

    assert len(records) == 3
    assert all(record.get("size") is None for record in records)
    assert records[2]["type_of_engine"] == []
