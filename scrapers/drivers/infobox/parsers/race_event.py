"""Helper class for parsing race event information from infobox cells."""

from typing import Any

from bs4 import Tag

from scrapers.base.error_handler import ErrorHandler
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


class RaceEventParser:
    """Handles parsing of race event fields (First race, Last race, etc.)."""

    def __init__(self, link_extractor: InfoboxLinkExtractor):
        """Initialize the race event parser.

        Args:
            link_extractor: Link extractor for extracting URLs from cells
        """
        self._link_extractor = link_extractor

    def parse_race_event(self, cell: Tag) -> list[dict[str, Any]]:
        """Parse race event fields like First race, Last race, First win, Last win.

        Returns a list of all links found in the cell.
        If no links are found, returns the text as a single-item list with text field.

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            List of dictionaries with 'text' and 'url' keys

        Raises:
            DomainParseError: If parsing fails
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        return ErrorHandler.run_domain_parse(
            lambda: self._parse_race_event_payload(cell, text),
            message=f"Nie udało się sparsować wydarzenia wyścigowego: {text!r}.",
            parser_name=self.__class__.__name__,
        )

    def _parse_race_event_payload(self, cell: Tag, text: str) -> list[dict[str, Any]]:
            links = self._link_extractor.extract_links(cell)

            # If we have links, return them
            if links:
                return links

            # If no links, return the text
            if text:
                return [{"text": text, "url": None}]

            return []
