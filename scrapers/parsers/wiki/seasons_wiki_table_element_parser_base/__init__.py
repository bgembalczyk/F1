"""seasons_wiki_table_element_parser_base package.

This package contains wiki-table element parsers for F1 season data.
``SeasonStandingsService`` is the canonical service entry-point for
season-standings table processing.
"""

from __future__ import annotations

from typing import Any

from bs4 import BeautifulSoup

from scrapers.parsers.wiki.seasons_wiki_table_element_parser_base.base import BaseSeasonParser


class SeasonStandingsService:
    """Orchestrates season-standings parsing across drivers and constructors.

    Wraps a :class:`BaseSeasonParser`-compatible standings parser and exposes
    a simple ``run()`` interface for higher-level consumers.
    """

    def __init__(self, parser: BaseSeasonParser) -> None:
        self._parser = parser

    def run(
        self,
        soup: BeautifulSoup,
        *,
        season_year: int | None = None,
    ) -> list[dict[str, Any]]:
        """Parse season-standings tables from *soup* and return domain records."""
        return self._parser.parse(soup, season_year=season_year)


__all__ = ["SeasonStandingsService"]
