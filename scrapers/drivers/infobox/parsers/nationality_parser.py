"""Helper class for parsing nationality from infobox cells."""

import re
from typing import Any
from typing import Dict
from typing import List
from typing import Union

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor


class NationalityParser:
    """Handles parsing of nationality information with optional year ranges."""

    def __init__(self, link_extractor: InfoboxLinkExtractor) -> None:
        """Initialize the nationality parser.
        
        Args:
            link_extractor: Link extractor instance for extracting URLs
        """
        self._link_extractor = link_extractor

    def parse_nationality(self, cell: Tag) -> Union[List[str], List[Dict[str, Any]]]:
        """Parse nationality field.

        Handles cases like:
        - "American or Italian" -> ["American", "Italian"]
        - "British" with link -> [{"text": "British", "url": "..."}]
        - "Federation of Rhodesia and Nyasaland (1963)" with year ranges -> structured data with years
        
        Args:
            cell: BeautifulSoup Tag representing the cell
            
        Returns:
            List of nationality strings OR list of dictionaries with text/url or nationality/years
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""

        # Check if there are year references (indicating nationality changed by season)
        has_years = re.search(r"\(\s*\d{4}", text)

        if has_years:
            return self._parse_nationality_with_years(cell)
        return self._parse_nationality_simple(cell, text)

    def _parse_nationality_with_years(self, cell: Tag) -> List[Dict[str, Any]]:
        """Parse structured nationality entries that include year information.

        Splits the cell HTML on <br> tags and extracts one nationality entry
        per part, including any associated year ranges.

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            List of dicts with 'nationality' and 'years' keys.
        """
        html = str(cell)
        parts = re.split(r"<br\s*/?>", html, flags=re.IGNORECASE)

        nationalities = []

        for part_html in parts:
            if not part_html.strip():
                continue

            part_soup = BeautifulSoup(part_html, "html.parser")
            part_text = clean_infobox_text(part_soup.get_text(" ", strip=True)) or ""

            nationality_name = re.sub(
                r"\s*\([^)]*\d{4}[^)]*\)", "", part_text,
            ).strip()

            years = self._extract_years_from_text(part_text)

            if nationality_name and years:
                nationalities.append(
                    {"nationality": nationality_name, "years": sorted(years)},
                )
            elif nationality_name:
                nationalities.append({"nationality": nationality_name, "years": []})

        return nationalities if nationalities else []

    @staticmethod
    def _extract_years_from_text(text: str) -> List[int]:
        """Extract all years (including ranges) from parenthesised patterns in text.

        Args:
            text: Text possibly containing patterns like "(1963)" or "(1965, 1967-1968)".

        Returns:
            Deduplicated list of integer years found in the text.
        """
        years: List[int] = []
        year_patterns = re.findall(r"\(([^)]*\d{4}[^)]*)\)", text)

        for year_pattern in year_patterns:
            for range_match in re.finditer(r"(\d{4})\s*[-–]\s*(\d{4})", year_pattern):
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                for year in range(start, end + 1):
                    if year not in years:
                        years.append(year)

            for year_match in re.finditer(r"\b(\d{4})\b", year_pattern):
                year = int(year_match.group(1))
                if year not in years:
                    years.append(year)

        return years

    def _parse_nationality_simple(
            self, cell: Tag, text: str,
    ) -> Union[List[str], List[Dict[str, Any]]]:
        """Parse nationality when no year information is present.

        Tries link-based extraction first; falls back to plain-text splitting.

        Args:
            cell: BeautifulSoup Tag representing the cell
            text: Pre-cleaned text content of the cell

        Returns:
            List of nationality dicts (with 'text'/'url') or plain strings.
        """
        nationality_links = self._extract_nationality_links(cell)

        if nationality_links:
            return [
                {"text": link.get("text", ""), "url": link.get("url")}
                for link in nationality_links
            ]

        return self._parse_nationality_from_text(text)

    def _extract_nationality_links(self, cell: Tag) -> List[Dict[str, Any]]:
        """Extract non-empty, non-reference links from the cell.

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            List of link dicts that represent actual nationality links.
        """
        links = self._link_extractor.extract_links(cell)
        return [
            link
            for link in links
            if (link.get("text") or "").strip()
            and not re.match(r"^\[\d+\]$", (link.get("text") or "").strip())
        ]

    @staticmethod
    def _parse_nationality_from_text(text: str) -> List[str]:
        """Split plain text on "or" to obtain individual nationality names.

        Args:
            text: Cleaned text from the nationality cell

        Returns:
            List of nationality strings with reference markers removed.
        """
        parts = re.split(r"\s+or\s+", text, flags=re.IGNORECASE)
        nationalities = []

        for part in parts:
            part = re.sub(r"\[\d+\]", "", part).strip()
            if part:
                nationalities.append(part)

        return nationalities if len(nationalities) > 1 else (nationalities or [])
