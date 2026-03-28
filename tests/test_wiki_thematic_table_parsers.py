from pathlib import Path

from bs4 import BeautifulSoup

from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser


def _load_fixture() -> BeautifulSoup:
    fixture = Path("tests/fixtures/wiki_tables/f1_thematic_tables.html").read_text()
    return BeautifulSoup(fixture, "html.parser")


def test_specialized_standings_parser_maps_columns() -> None:
    soup = _load_fixture()
    table = soup.find_all("table", class_="wikitable")[0]
    parsed = ArticleTablesParser(include_source_table=True).parse_table(table)
    assert parsed is not None
    assert parsed["table_type"] == "standings"
    assert parsed["domain_column_map"]["Pos."] == "pos"
    assert parsed["domain_rows"][0]["driver"] == "Max Verstappen"


def test_specialized_race_results_parser_maps_columns() -> None:
    soup = _load_fixture()
    table = soup.find_all("table", class_="wikitable")[1]
    parsed = ArticleTablesParser(include_source_table=True).parse_table(table)
    assert parsed is not None
    assert parsed["table_type"] == "race_results"
    assert parsed["domain_rows"][0]["round"] == "1"
    assert parsed["domain_rows"][0]["winning_driver"] == "Max Verstappen"


def test_specialized_lap_records_parser_maps_columns() -> None:
    soup = _load_fixture()
    table = soup.find_all("table", class_="wikitable")[2]
    parsed = ArticleTablesParser(include_source_table=True).parse_table(table)
    assert parsed is not None
    assert parsed["table_type"] == "lap_records"
    assert parsed["domain_rows"][0]["time"] == "1:27.097"
    assert parsed["domain_rows"][0]["driver"] == "Lewis Hamilton"


def test_article_tables_parser_fallback_to_generic_type() -> None:
    soup = _load_fixture()
    table = soup.find_all("table", class_="wikitable")[3]
    parsed = ArticleTablesParser(include_source_table=True).parse_table(table)
    assert parsed is not None
    assert parsed["table_type"] == "wiki_table"
    assert "domain_rows" not in parsed
