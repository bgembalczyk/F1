"""Helper class for parsing teams information from infobox cells."""

from typing import Any

from bs4 import Tag

from models.services.helpers import split_delimited_text
from scrapers.helpers.text_normalization import clean_infobox_text
from scrapers.infobox.parsers.drivers.link_extractor import InfoboxLinkExtractor
from scrapers.infobox.parsers.base_field_parser import BaseInfoboxFieldParser
from scrapers.infobox.extraction.extractor import InfoboxLinkExtractor


class TeamsParser(BaseInfoboxFieldParser):
    """Handles parsing of teams information."""

    def __init__(
        self,
        link_extractor: InfoboxLinkExtractor,
        *,
        include_urls: bool,
    ):
        """Initialize the teams parser.

        Args:
            link_extractor: Link extractor for extracting URLs from cells
            include_urls: Whether to include URL information
        """
        self._link_extractor = link_extractor
        self._include_urls = include_urls

    def parse(self, raw: Tag) -> list[Any]:
        return self.parse_teams(raw)

    def parse_teams(self, cell: Tag) -> list[Any]:
        """Parse teams field.

        If URLs are included, returns links; otherwise returns text split by commas.

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            List of team links (if include_urls is True) or list of team names
        """
        if self._include_urls:
            return self._link_extractor.extract_links(raw)
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        return split_delimited_text(text, pattern=r",")

    def parse_teams(self, cell: Tag) -> list[Any]:
        """Backward-compatible wrapper around :meth:`parse`."""
        return self.parse(raw)


__all__ = ["TeamsParser"]
