"""Helper class for parsing championships and class wins from infobox cells."""

import re
from typing import Any

from bs4 import Tag

from scrapers.base.error_handler import ErrorHandler
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.year_extraction import YearExtractor
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


class ChampionshipsParser:
    """Handles parsing of championships and class wins information."""

    def __init__(self, link_extractor: InfoboxLinkExtractor):
        """Initialize the championships parser.

        Args:
            link_extractor: Link extractor for extracting URLs from cells
        """
        self._link_extractor = link_extractor

    def parse_championships(self, cell: Tag) -> dict[str, Any]:
        """Parse championships count with links.

        Handles cases like:
        - "1 (2014)" -> {count: 1, championships: [{text: "2014", url: ...}]}
        - "2 (2015, 2016)" -> {count: 2, championships: [...]}

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            Dictionary with 'count' and 'championships' keys

        Raises:
            DomainParseError: If parsing fails
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        return ErrorHandler.run_domain_parse(
            lambda: self._parse_championships_payload(cell, text),
            message=f"Nie udało się sparsować mistrzostw: {text!r}.",
            parser_name=self.__class__.__name__,
        )

    def _parse_championships_payload(self, cell: Tag, text: str) -> dict[str, Any]:
            # Extract count
            count_match = re.search(r"^(\d+)", text)
            count = int(count_match.group(1)) if count_match else 0

            # Extract links from parentheses - treat as simple list of links
            championships = self._link_extractor.extract_links(cell)

            return {"count": count, "championships": championships}

    def parse_class_wins(self, cell: Tag) -> dict[str, Any]:
        """Parse class wins count with year and link information.

        Similar to championships, handles cases like:
        - "6 (1969, 1975, 1976)" -> {count: 6, wins: [{year: 1969, url: ...}, ...]}

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            Dictionary with 'count' and 'wins' keys

        Raises:
            DomainParseError: If parsing fails
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        return ErrorHandler.run_domain_parse(
            lambda: self._parse_class_wins_payload(cell, text),
            message=f"Nie udało się sparsować zwycięstw klasowych: {text!r}.",
            parser_name=self.__class__.__name__,
        )

    def _parse_class_wins_payload(self, cell: Tag, text: str) -> dict[str, Any]:
            # Extract count
            count_match = re.search(r"^(\d+)", text)
            count = int(count_match.group(1)) if count_match else 0

            # Extract year links
            wins = []
            links = self._link_extractor.extract_links(cell)

            # Build year -> url mapping using shared utility
            year_to_url = YearExtractor.build_year_to_url_map(links)

            # Extract all years from text (typically in parentheses or <small> tag)
            # Check <small> tag first
            small_tag = cell.find("small")
            if small_tag:
                small_text = (
                    clean_infobox_text(small_tag.get_text(" ", strip=True)) or ""
                )
                for year_match in re.finditer(r"\b(\d{4})\b", small_text):
                    year = int(year_match.group(1))
                    wins.append({"year": year, "url": year_to_url.get(year)})
            else:
                # Fallback to extracting from parentheses in main text
                paren_match = re.search(r"\(([^)]+)\)", text)
                if paren_match:
                    paren_content = paren_match.group(1)
                    for year_match in re.finditer(r"\b(\d{4})\b", paren_content):
                        year = int(year_match.group(1))
                        wins.append({"year": year, "url": year_to_url.get(year)})

            return {"count": count, "wins": wins}
