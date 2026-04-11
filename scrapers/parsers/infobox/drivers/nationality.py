"""Helper class for parsing nationality from infobox cells."""

from typing import Any

from bs4 import BeautifulSoup
from bs4 import Tag

from scrapers.helpers.text_normalization import clean_infobox_text
from scrapers.infobox.extraction.extractor import InfoboxLinkExtractor
from scrapers.parsers.infobox.constants import BR_SPLIT_RE
from scrapers.parsers.infobox.constants import HAS_YEARS_RE
from scrapers.parsers.infobox.constants import JUST_REF_MARKER_RE
from scrapers.parsers.infobox.constants import OR_SPLIT_RE
from scrapers.parsers.infobox.constants import REF_MARKER_RE
from scrapers.parsers.infobox.constants import YEAR_PAREN_RE
from scrapers.parsers.infobox.constants import YEAR_PATTERNS_RE
from scrapers.parsers.infobox.constants import YEAR_RANGE_RE_NAT
from scrapers.parsers.infobox.constants import YEAR_RE
from scrapers.infobox.parsers.drivers import constants
from scrapers.infobox.parsers.drivers.link_extractor import InfoboxLinkExtractor
from scrapers.infobox.parsers.base_field_parser import BaseInfoboxFieldParser


class NationalityParser(BaseInfoboxFieldParser):
    """Handles parsing of nationality information with optional year ranges."""

    def __init__(self, link_extractor: InfoboxLinkExtractor) -> None:
        """Initialize the nationality parser.

        Args:
            link_extractor: Link extractor instance for extracting URLs
        """
        self._link_extractor = link_extractor

    def parse(self, raw: Tag) -> list[str] | list[dict[str, Any]]:
        return self._parse_nationality(raw)

    def _parse_nationality(self, cell: Tag) -> list[str] | list[dict[str, Any]]:
        """Parse nationality field.

        Handles cases like:
        - "American or Italian" -> ["American", "Italian"]
        - "British" with link -> [{"text": "British", "url": "..."}]
        - "Federation of Rhodesia and Nyasaland (1963)" -> structured data

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            List of strings or dictionaries with text/url or nationality/years
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""

        # Check if there are year references (indicating nationality changed by season)
        has_years = HAS_YEARS_RE.search(text)

        if has_years:
            return self._parse_nationality_with_years(raw)
        return self._parse_nationality_simple(raw, text)

    def parse_nationality(self, cell: Tag) -> list[str] | list[dict[str, Any]]:
        """Backward-compatible wrapper around :meth:`parse`."""
        return self.parse(raw)

    def _parse_nationality_with_years(self, cell: Tag) -> list[dict[str, Any]]:
        """Parse structured nationality entries that include year information.

        Splits the cell HTML on <br> tags and extracts one nationality entry
        per part, including any associated year ranges.

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            List of dicts with 'nationality' and 'years' keys.
        """
        html = str(cell)
        parts = BR_SPLIT_RE.split(html)

        nationalities = []

        for part_html in parts:
            if not part_html.strip():
                continue

            part_soup = BeautifulSoup(part_html, "html.parser")
            part_text = clean_infobox_text(part_soup.get_text(" ", strip=True)) or ""

            nationality_name = YEAR_PAREN_RE.sub("", part_text).strip()

            years = self._extract_years_from_text(part_text)

            if nationality_name and years:
                nationalities.append(
                    {"nationality": nationality_name, "years": sorted(years)},
                )
            elif nationality_name:
                nationalities.append({"nationality": nationality_name, "years": []})

        return nationalities or []

    @classmethod
    def _extract_years_from_text(cls, text: str) -> list[int]:
        """Extract all years (including ranges) from parenthesised patterns in text.

        Args:
            text: Text with patterns like "(1963)" or "(1965, 1967-1968)".

        Returns:
            Deduplicated list of integer years found in the text.
        """
        years_dict: dict[int, None] = {}
        year_patterns = YEAR_PATTERNS_RE.findall(text)

        for year_pattern in year_patterns:
            for range_match in YEAR_RANGE_RE_NAT.finditer(year_pattern):
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                for year in range(start, end + 1):
                    years_dict[year] = None

            for year_match in YEAR_RE.finditer(year_pattern):
                years_dict[int(year_match.group(1))] = None

        return list(years_dict.keys())

    def _parse_nationality_simple(
        self,
        cell: Tag,
        text: str,
    ) -> list[str] | list[dict[str, Any]]:
        """Parse nationality when no year information is present.

        Tries link-based extraction first; falls back to plain-text splitting.

        Args:
            cell: BeautifulSoup Tag representing the cell
            text: Pre-cleaned text content of the cell

        Returns:
            List of nationality dicts (with 'text'/'url') or plain strings.
        """
        nationality_links = self._extract_nationality_links(raw)

        if nationality_links:
            return [
                {"text": link.get("text", ""), "url": link.get("url")}
                for link in nationality_links
            ]

        return self._parse_nationality_from_text(text)

    def _extract_nationality_links(self, cell: Tag) -> list[dict[str, Any]]:
        """Extract non-empty, non-reference links from the cell.

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            List of link dicts that represent actual nationality links.
        """
        links = self._link_extractor.extract_links(raw)
        return [
            link
            for link in links
            if (link.get("text") or "").strip()
            and not JUST_REF_MARKER_RE.match((link.get("text") or "").strip())
        ]

    @staticmethod
    def _parse_nationality_from_text(text: str) -> list[str]:
        """Split plain text on "or" to obtain individual nationality names.

        Args:
            text: Cleaned text from the nationality cell

        Returns:
            List of nationality strings with reference markers removed.
        """
        parts = OR_SPLIT_RE.split(text)
        nationalities = []

        for raw_part in parts:
            cleaned_part = REF_MARKER_RE.sub("", raw_part).strip()
            if cleaned_part:
                nationalities.append(cleaned_part)

        return nationalities if len(nationalities) > 1 else (nationalities or [])


__all__ = [
    "NationalityParser",
]
