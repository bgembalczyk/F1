from __future__ import annotations

from scrapers.parsers.wiki.base_nested_section.nested_section.seasons import (
    SeasonsSectionParser,
)
from scrapers.seasons.list_scraper_seasons import SeasonsSectionParser
from scrapers.seasons.list_scraper_seasons import SeasonsTableMapper


def test_seasons_table_parser_matches_minimal_required_headers() -> None:
    parser = SeasonsTableMapper()

    assert parser.matches(["Season", "Races", "Winners"], {}) is True
    assert parser.matches(["Season"], {}) is False


def test_seasons_table_parser_maps_only_supported_headers() -> None:
    parser = SeasonsTableMapper()

    assert parser.map_columns(["Season", "Races", "Ignored"]) == {
        "Season": "season",
        "Races": "races",
    }


def test_seasons_section_parser_rewrites_table_elements_recursively() -> None:
    parser = SeasonsSectionParser()
    payload = {
        "sub_sections": [
            {
                "elements": [
                    {
                        "kind": "table",
                        "data": {
                            "headers": ["Season", "Races"],
                            "rows": [{"Season": {"text": "2023"}, "Races": "22"}],
                        },
                    },
                ],
                "sub_sections": [],
            },
        ],
    }

    parser._apply_seasons_table_parser(payload)

    nested_table = payload["sub_sections"][0]["elements"][0]["data"]
    assert nested_table["table_type"] == "seasons_list"
    assert nested_table["domain_rows"][0]["season"]["text"] == "2023"
    assert nested_table["domain_rows"][0]["races"] == "22"
