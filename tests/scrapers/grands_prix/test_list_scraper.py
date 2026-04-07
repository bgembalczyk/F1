# ruff: noqa: E501, PLR2004, SLF001
from scrapers.grands_prix.list_scraper import ByRaceTitleSubSectionParser
from scrapers.grands_prix.list_scraper import GrandsPrixTableParser


def test_grands_prix_table_parser_matches_required_headers() -> None:
    parser = GrandsPrixTableParser()
    assert parser.matches(["Race title", "Years held"], {}) is True
    assert parser.matches(["Race title", "Years held", "Extra"], {}) is True


def test_grands_prix_table_parser_does_not_match_missing_headers() -> None:
    parser = GrandsPrixTableParser()
    assert parser.matches(["Race title"], {}) is False
    assert parser.matches([], {}) is False


def test_grands_prix_table_parser_map_columns_filters_known() -> None:
    parser = GrandsPrixTableParser()
    result = parser.map_columns(["Race title", "Years held", "Unknown"])
    assert "Race title" in result
    assert "Years held" in result
    assert "Unknown" not in result


def test_by_race_title_parse_group_returns_dict() -> None:
    parser = ByRaceTitleSubSectionParser()

    class _Stub:
        def apply_to_payload(self, _payload):
            pass

    parser._table_parser = _Stub()
    result = parser.parse_group([], context=None)
    assert isinstance(result, dict)
