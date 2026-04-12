from __future__ import annotations

from scrapers.parsers.section.legacy_lists.tyres import ManufacturersSectionParser
from scrapers.parsers.section.legacy_lists.tyres import TyreManufacturersBySeasonTableMapper
from scrapers.list_scraper_tyres import TyreManufacturersScraper
from scrapers.tyres.list_scraper_tyres import TyreManufacturersScraper


def test_table_parser_matches_only_required_headers_subset() -> None:
    parser = TyreManufacturersBySeasonTableMapper()

    assert parser.matches(["Season", "Manufacturer 1", "Wins", "Extra"], {})
    assert not parser.matches(["Season", "Manufacturer 2", "Wins"], {})


def test_table_parser_maps_only_known_headers() -> None:
    parser = TyreManufacturersBySeasonTableMapper()

    mapped = parser.map_columns(["Season", "Manufacturer 4", "Wins", "Unknown"])

    assert mapped == {
        "Season": "seasons",
        "Manufacturer 4": "manufacturers",
        "Wins": "wins",
    }


def test_scraper_wires_manufacturers_section_parser() -> None:
    scraper = TyreManufacturersScraper()

    assert isinstance(scraper.section_parser, ManufacturersSectionParser)
    assert (
        scraper.body_content_parser.content_text_parser.section_parser
        is scraper.section_parser
    )
