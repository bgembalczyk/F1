from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from scrapers.helpers.transformers import append_transformer
from scrapers.options import ScraperOptions
from scrapers.parsers.table.red_flagged_races import WIKIPEDIA_BASE_URL
from scrapers.parsers.table.red_flagged_races import BaseRedFlaggedRacesTableMapper
from scrapers.parsers.table.red_flagged_races import NonChampionshipsRacesTableMapper
from scrapers.parsers.table.red_flagged_races import WorldChampionshipsRacesTableMapper
from scrapers.parsers.table.red_flagged_races import build_full_url
from scrapers.parsers.table.red_flagged_races import extract_rich_cell
from scrapers.parsers.table.red_flagged_races import map_drivers_cell
from scrapers.parsers.table.red_flagged_races import map_winner_cell
from scrapers.parsers.table.red_flagged_races import try_int
from scrapers.parsers.table.red_flagged_races_wiki_table import WIKIPEDIA_BASE_URL
from scrapers.parsers.table.red_flagged_races_wiki_table import build_full_url
from scrapers.parsers.table.red_flagged_races_wiki_table import extract_rich_cell
from scrapers.parsers.table.red_flagged_races_wiki_table import map_drivers_cell
from scrapers.parsers.table.red_flagged_races_wiki_table import map_winner_cell
from scrapers.parsers.table.red_flagged_races_wiki_table import try_int
from scrapers.parsers.wiki.body_content import BodyContentAssembler
from scrapers.parsers.wiki.red_flagged_races import RedFlaggedRacesSectionParser
from scrapers.scraper_wiki import WikiScraper
from scrapers.source_catalog import RED_FLAGGED_RACES
from scrapers.transformers.record.failed_to_make_restart import (
    FailedToMakeRestartTransformer,
)


class RedFlaggedRacesScraper(WikiScraper):
    _SUPPORTED_EXPORT_SCOPES = {"all", "world_championship", "non_championship"}
    url = RED_FLAGGED_RACES.base_url

    def __init__(
        self,
        *,
        options: ScraperOptions | None = None,
        export_scope: str = "all",
    ) -> None:
        if export_scope not in self._SUPPORTED_EXPORT_SCOPES:
            msg = (
                f"Unsupported export_scope='{export_scope}' for "
                f"{self.__class__.__name__}"
            )
            raise ValueError(msg)
        super().__init__(
            options=append_transformer(options, FailedToMakeRestartTransformer()),
        )
        self._export_scope = export_scope
        parser = RedFlaggedRacesSectionParser()
        self.section_parser = parser
        self.body_content_parser.content_text_parser.section_parser = parser

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        body_content = BodyContentAssembler.find_body_content(soup)
        parsed = self.body_content_parser.parse(body_content) if body_content else {}
        world_records = RedFlaggedRacesSectionParser.collect_rows(
            parsed,
            table_type="red_flagged_world_championship_races",
        )
        non_championship_records = RedFlaggedRacesSectionParser.collect_rows(
            parsed,
            table_type="red_flagged_non_championship_races",
        )
        if self._export_scope == "world_championship":
            return world_records
        if self._export_scope == "non_championship":
            return non_championship_records
        return [*world_records, *non_championship_records]


__all__ = [
    "WIKIPEDIA_BASE_URL",
    "build_full_url",
    "try_int",
    "extract_rich_cell",
    "map_winner_cell",
    "map_drivers_cell",
    "BaseRedFlaggedRacesTableMapper",
    "WorldChampionshipsRacesTableMapper",
    "NonChampionshipsRacesTableMapper",
    "RedFlaggedRacesSectionParser",
    "RedFlaggedRacesScraper",
]
