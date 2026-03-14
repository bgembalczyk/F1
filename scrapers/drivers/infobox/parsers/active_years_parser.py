"""Helper class for parsing active years from infobox cells."""

from typing import Any

from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.base.helpers.year_extraction import YearExtractor
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


class ActiveYearsParser:
    """Handles parsing of active years information."""

    def __init__(self, link_extractor: InfoboxLinkExtractor):
        """Initialize the active years parser.

        Args:
            link_extractor: Link extractor for extracting URLs from cells
        """
        self._link_extractor = link_extractor

    def parse_active_years(self, cell: Tag) -> list[dict[str, Any]]:
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

        # Build a map of year -> link using shared utility
        year_to_link = YearExtractor.build_year_to_url_map(links)

        # Extract all years and ranges from text using shared utility
        years_set = YearExtractor.extract_years_from_text(text)

        # Try to interpolate URLs for missing years using shared utility
        year_to_link = YearExtractor.interpolate_urls(years_set, year_to_link)

        # Build result list
        result = []
        for year in sorted(years_set):
            result.append({"year": year, "url": year_to_link.get(year)})

        return result
