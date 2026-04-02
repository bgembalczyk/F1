from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from scrapers.base.list.scraper import F1ListScraper
from scrapers.base.single_wiki_article.section_selection_strategy import (
    WikipediaSectionByIdSelectionStrategy,
)
from scrapers.base.source_catalog import CONSTRUCTORS_LIST
from scrapers.constructors.current_constructors_list import CurrentConstructorsListScraper
from scrapers.constructors.former_constructors_list import FormerConstructorsListScraper
from scrapers.constructors.indianapolis_only_constructors_list import (
    IndianapolisOnlyConstructorsListScraper,
)
from scrapers.constructors.privateer_teams_list import PrivateerTeamsListScraper
from scrapers.constructors.sections.list_section import CurrentConstructorsSectionParser
from scrapers.constructors.sections.list_section import FormerConstructorsSectionParser
from scrapers.constructors.privateer_teams_list import PrivateerTeamsSectionParser


class ConstructorsListScraper(F1ListScraper):
    """Combined constructors list scraper for all constructors list sections."""

    url = CONSTRUCTORS_LIST.base_url
    combined_scraper_classes = (
        CurrentConstructorsListScraper,
        FormerConstructorsListScraper,
        IndianapolisOnlyConstructorsListScraper,
        PrivateerTeamsListScraper,
    )

    def _parse_soup(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        selector = WikipediaSectionByIdSelectionStrategy(domain="constructors")
        records: list[dict[str, Any]] = []

        current_section = selector.extract_section_by_id(
            soup,
            CurrentConstructorsListScraper.CONFIG.section_id,
            domain="constructors",
        )
        if current_section is not None:
            current_parser = CurrentConstructorsSectionParser(
                config=CurrentConstructorsListScraper.CONFIG,
                section_label=CurrentConstructorsListScraper.section_label,
                include_urls=self.include_urls,
                normalize_empty_values=self.normalize_empty_values,
            )
            records.extend(current_parser.parse(current_section).records)

        former_section = selector.extract_section_by_id(
            soup,
            FormerConstructorsListScraper.CONFIG.section_id,
            domain="constructors",
        )
        if former_section is not None:
            former_parser = FormerConstructorsSectionParser(
                config=FormerConstructorsListScraper.CONFIG,
                section_label=FormerConstructorsListScraper.section_label,
                include_urls=self.include_urls,
                normalize_empty_values=self.normalize_empty_values,
            )
            records.extend(former_parser.parse(former_section).records)

        privateer_section = selector.extract_section_by_id(
            soup,
            PrivateerTeamsListScraper.section_id,
            domain="constructors",
        )
        if privateer_section is not None:
            privateer_parser = PrivateerTeamsSectionParser()
            privateer_records = privateer_parser.parse(privateer_section).get("items", [])
            if not self.include_urls:
                for record in privateer_records:
                    if isinstance(record, dict):
                        record.pop("team_url", None)
            else:
                for record in privateer_records:
                    if not isinstance(record, dict):
                        continue
                    url = record.get("team_url")
                    if isinstance(url, str) and url.startswith("/"):
                        record["team_url"] = self._full_url(url)
            records.extend(privateer_records)

        return records


if __name__ == "__main__":
    from scrapers.base.deprecated_entrypoint import run_deprecated_entrypoint

    run_deprecated_entrypoint()
