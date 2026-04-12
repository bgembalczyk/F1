from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any


if TYPE_CHECKING:
    from bs4 import BeautifulSoup
from scrapers.parsers.wiki.section.sponsorship import SponsorshipSectionParser


class TeamLiveriesTableAdapter:
    """Adapter tabeli sekcji zespołu do istniejącego parsera domenowego."""

    def __init__(self, *, section_table_parser: SponsorshipSectionParser) -> None:
        self._section_table_parser = section_table_parser

    def parse(
        self,
        soup: BeautifulSoup,
        *,
        section_id: str,
        team: str,
    ) -> list[dict[str, Any]]:
        return self._parse_team_table(
            soup,
            section_id=section_id,
            team=team,
        )

    def _parse_team_table(
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


__all__ = ["TeamLiveriesTableAdapter"]
