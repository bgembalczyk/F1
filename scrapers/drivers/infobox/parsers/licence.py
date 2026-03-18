"""Helper class for parsing racing licence information."""

from typing import Any

from bs4 import Tag

from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor
from scrapers.drivers.infobox.parsers.year import YearParser


class LicenceParser:
    """Handles parsing of racing licence information."""

    def __init__(self, link_extractor: InfoboxLinkExtractor):
        """Initialize the licence parser.

        Args:
            link_extractor: Link extractor for extracting URLs from cells
        """
        self._link_extractor = link_extractor

    def parse_racing_licence(self, cell: Tag) -> list[dict[str, Any]]:
        """Parse 'Racing licence' field.

        Example: "FIA Gold (until 2019)" and "FIA Platinum (2020-)"
        -> [{licence: {...}, years: {...}}, {licence: {...}, years: {...}}]
        """
        try:
            licence_links = self._extract_licence_links(cell)
            if not licence_links:
                return []

            year_spans = cell.find_all("span", style=lambda x: x and "font-size" in x)

            licences = []
            for licence_link in licence_links:
                licence_entry: dict[str, Any] = {
                    "licence": licence_link,
                    "years": {"start": None, "end": None},
                }

                licence_tag = self._find_licence_tag(cell, licence_link)
                if licence_tag and year_spans:
                    licence_tag_map = self._build_licence_tag_map(
                        cell,
                        licence_links,
                        licence_link,
                    )
                    years = self._find_year_for_licence(
                        licence_tag,
                        year_spans,
                        licence_tag_map,
                    )
                    if years is not None:
                        licence_entry["years"] = years

                licences.append(licence_entry)

            return licences
        except (TypeError, ValueError) as exc:
            text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
            msg = f"Nie udało się sparsować licencji wyścigowej: {text!r}."
            raise DomainParseError(
                msg,
                cause=exc,
            ) from exc

    def _extract_licence_links(self, cell: Tag) -> list[dict[str, Any]]:
        """Extract and return licence links, excluding file/image links.

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            List of link dicts for non-file links.
        """
        all_links = self._link_extractor.extract_links(cell)
        return [
            link for link in all_links if "/file:" not in link.get("url", "").lower()
        ]

    def _find_licence_tag(self, cell: Tag, licence_link: dict[str, Any]) -> Tag | None:
        """Find the <a> DOM element corresponding to the given licence link dict.

        Args:
            cell: BeautifulSoup Tag representing the cell
            licence_link: Link dict with 'text' and 'url' keys

        Returns:
            Matching <a> Tag or None if not found.
        """
        licence_text = licence_link.get("text", "")
        licence_url = licence_link.get("url", "")

        for a_tag in cell.find_all("a"):
            if clean_infobox_text(a_tag.get_text(strip=True)) != licence_text:
                continue
            a_href = a_tag.get("href", "") or ""
            if licence_url and a_href not in licence_url:
                continue
            if "/file:" not in a_href.lower():
                return a_tag

        return None

    def _build_licence_tag_map(
        self,
        cell: Tag,
        licence_links: list[dict[str, Any]],
        current_link: dict[str, Any],
    ) -> dict[str, Tag]:
        """Build a text-to-tag mapping for all licence links except the current one.

        Args:
            cell: BeautifulSoup Tag representing the cell
            licence_links: All licence link dicts for this cell
            current_link: The link being processed (excluded from the map)

        Returns:
            Dict mapping licence text to its <a> Tag.
        """
        all_a_tags = cell.find_all("a")
        licence_tag_map: dict[str, Tag] = {}

        for other_link in licence_links:
            if other_link == current_link:
                continue
            other_text = other_link.get("text", "")
            if not other_text or other_text in licence_tag_map:
                continue
            for a_tag in all_a_tags:
                if clean_infobox_text(a_tag.get_text(strip=True)) == other_text:
                    a_href = a_tag.get("href", "") or ""
                    if "/file:" not in a_href.lower():
                        licence_tag_map[other_text] = a_tag
                        break

        return licence_tag_map

    def _find_year_for_licence(
        self,
        licence_tag: Tag,
        year_spans: list[Tag],
        licence_tag_map: dict[str, Tag],
    ) -> dict[str, Any] | None:
        """Find and parse the year span that immediately follows the given licence tag.

        A year span is considered to belong to *licence_tag* when it comes after
        that tag in document order AND no other licence tag appears between them.

        Args:
            licence_tag: The <a> Tag for the current licence
            year_spans: All year-bearing <span> elements found in the cell
            licence_tag_map: Mapping of other licence texts to their <a> Tags

        Returns:
            Parsed year dict or None if no matching span is found.
        """
        for year_span in year_spans:
            if not self._is_element_before(licence_tag, year_span):
                continue

            has_licence_between = any(
                self._is_element_before(licence_tag, other_tag)
                and self._is_element_before(other_tag, year_span)
                for other_tag in licence_tag_map.values()
            )
            if not has_licence_between:
                year_text = year_span.get_text(strip=True)
                return YearParser.parse_licence_years(year_text)

        return None

    @staticmethod
    def _is_element_before(elem1: Tag, elem2: Tag) -> bool:
        """Check if elem1 comes before elem2 in document order.

        Uses BeautifulSoup's built-in ordering to compare positions efficiently.
        """
        # Get all elements in order by traversing once
        # Find the first occurrence - if it's elem1, then elem1 is before elem2
        elem1_parents = list(elem1.parents)
        elem2_parents = list(elem2.parents)

        # Find deepest common parent
        common_parent = None
        for p1 in elem1_parents:
            if p1 in elem2_parents:
                common_parent = p1
                break

        if common_parent is None:
            return False

        # Use BeautifulSoup's generator to avoid creating a full list
        for descendant in common_parent.descendants:
            if descendant is elem1:
                return True
            if descendant is elem2:
                return False

        return False
