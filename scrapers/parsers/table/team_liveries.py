from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.wiki.parsers.elements.table import TableParser

if TYPE_CHECKING:
    from bs4 import BeautifulSoup



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




__all__ = ["TeamLiveriesTableParser"]
