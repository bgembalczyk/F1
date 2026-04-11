from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.paren_classifier import ParenClassifier
from scrapers.parsers.section.sponsorship import SponsorshipSectionParser
from scrapers.parsers.table.team_liveries import TeamLiveriesTableParser
from scrapers.parsers.wiki.base import WikiSectionParserBase

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class TeamLiveriesSectionParser(WikiSectionParserBase):
    """Parser sekcji artykułu sponsorowanych malowań F1."""

    def __init__(
        self,
        *,
        url: str,
        include_urls: bool,
        normalize_empty_values: bool,
        splitter,
        classifier: ParenClassifier | None = None,
    ) -> None:
        self._base_parser = SponsorshipSectionParser(
            url=url,
            include_urls=include_urls,
            normalize_empty_values=normalize_empty_values,
            splitter=splitter,
            classifier=classifier,
        )
        self._table_parser = TeamLiveriesTableParser(
            section_table_parser=self._base_parser,
        )

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        seen_sections: set[str] = set()
        for heading, headline in self._base_parser.collect_section_headings(soup):
            section_id = self._base_parser.section_id_if_new(headline, seen_sections)
            if not section_id:
                continue
            if not self._base_parser.section_has_table(heading, headline):
                continue
            team = self._base_parser.team_name_from_heading(heading, headline)
            liveries = self._parse_single_team_section(
                soup,
                section_id=section_id,
                team=team,
            )
            if liveries is None:
                continue
            records.append({"team": team, "liveries": liveries})
        return records

    # DEPRECATED(2026-04): alias tymczasowy; używaj parse(...).
    # Remove after all call-sites migrate to parse().
    def parse_sections(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        return self.parse(soup)

    def _parse_single_team_section(
        self,
        soup: BeautifulSoup,
        *,
        section_id: str,
        team: str,
    ) -> list[dict[str, Any]] | None:
        try:
            return self._table_parser.parse_team_table(
                soup,
                section_id=section_id,
                team=team,
            )
        except RuntimeError:
            return None


__all__ = ["TeamLiveriesSectionParser"]
