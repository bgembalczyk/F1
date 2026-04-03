from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from bs4 import BeautifulSoup

from scrapers.sponsorship_liveries.parsers.section import SponsorshipSectionParser
from scrapers.wiki.parsers.elements.table import TableParser
from scrapers.wiki.parsers.sections.section import SectionParser

if TYPE_CHECKING:
    from scrapers.sponsorship_liveries.helpers.paren_classifier import ParenClassifier


class TeamLiveriesTableParser(TableParser):
    """Adapter tabeli sekcji zespołu do istniejącego parsera domenowego."""

    def __init__(self, *, section_table_parser: SponsorshipSectionParser) -> None:
        super().__init__()
        self._section_table_parser = section_table_parser

    def parse_team_table(
        self,
        soup: BeautifulSoup,
        *,
        section_id: str,
        team: str,
    ) -> list[dict[str, Any]]:
        return self._section_table_parser.parse_section_table(
            soup,
            section_id=section_id,
            team=team,
        )


class TeamLiveriesSectionParser(SectionParser):
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
        super().__init__()
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

    def parse_sections(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
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
