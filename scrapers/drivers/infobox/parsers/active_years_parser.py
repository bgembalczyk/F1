"""Helper class for parsing active years from infobox cells."""

import re
from typing import Any
from typing import Dict
from typing import List

from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor
from scrapers.drivers.infobox.parsers.year_parser import YearParser


class ActiveYearsParser:
    """Handles parsing of active years information."""

    def __init__(self, link_extractor: InfoboxLinkExtractor):
        """Initialize the active years parser.
        
        Args:
            link_extractor: Link extractor for extracting URLs from cells
        """
        self._link_extractor = link_extractor

    def parse_active_years(self, cell: Tag) -> List[Dict[str, Any]]:
        """Parse active years as a list of individual seasons with links.

        Handles cases like:
        - Individual years: 2002, 2005, 2007, 2008
        - Ranges: 2007-2008 (interpolates missing links)
        
        Args:
            cell: BeautifulSoup Tag representing the cell
            
        Returns:
            List of dictionaries with 'year' and 'url' keys
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        links = self._link_extractor.extract_links(cell)

        # Build a map of year -> link
        year_to_link: Dict[int, str | None] = {}
        for link in links:
            link_text = link.get("text", "")
            year_match = re.search(r"\b(\d{4})\b", link_text)
            if year_match:
                year = int(year_match.group(1))
                year_to_link[year] = link.get("url")

        # Extract all years and ranges from text
        years_set: set[int] = set()

        # Find ranges like "2007-2008" or "2007–2008"
        for match in re.finditer(r"\b(\d{4})\s*[-–]\s*(\d{2,4})\b", text):
            start = int(match.group(1))
            end_text = match.group(2)
            if len(end_text) == 2:
                end = (start // 100) * 100 + int(end_text)
            else:
                end = int(end_text)
            for year in range(start, end + 1):
                years_set.add(year)

        # Find individual years
        for match in re.finditer(r"\b(\d{4})\b", text):
            year = int(match.group(1))
            years_set.add(year)

        # Try to interpolate URLs for missing years
        if len(year_to_link) >= 2:
            # Detect URL pattern
            url_pattern = YearParser.detect_url_pattern(year_to_link)
            if url_pattern:
                for year in years_set:
                    if year not in year_to_link:
                        year_to_link[year] = url_pattern.replace("{year}", str(year))

        # Build result list
        result = []
        for year in sorted(years_set):
            result.append({"year": year, "url": year_to_link.get(year)})

        return result
