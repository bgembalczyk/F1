"""Helper class for parsing racing licence information."""

from typing import Any
from typing import Dict
from typing import List

from bs4 import Tag

from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor
from scrapers.drivers.infobox.parsers.year_parser import YearParser


class LicenceParser:
    """Handles parsing of racing licence information."""

    def __init__(self, link_extractor: InfoboxLinkExtractor):
        """Initialize the licence parser.

        Args:
            link_extractor: Link extractor for extracting URLs from cells
        """
        self._link_extractor = link_extractor

    def parse_racing_licence(self, cell: Tag) -> List[Dict[str, Any]]:
        """Parse 'Racing licence' field.

        Example: "FIA Gold (until 2019)" and "FIA Platinum (2020–)"
        -> [{licence: {...}, years: {start: None, end: 2019}}, {licence: {...}, years: {start: 2020, end: None}}]
        """
        try:
            # Extract all links from the cell first, filtering out image/file links
            all_links = self._link_extractor.extract_links(cell)
            # Filter out links to files (images, etc.) - they typically contain "File:" in URL
            licence_links = [
                link
                for link in all_links
                if not (link.get("url", "").lower().find("/file:") >= 0)
            ]

            if not licence_links:
                return []

            # Find all <span> tags with year information (font-size styling)
            year_spans = cell.find_all("span", style=lambda x: x and "font-size" in x)

            licences = []

            # Strategy: For each licence link, find the nearest year span that comes after it
            for licence_link in licence_links:
                licence_entry = {
                    "licence": licence_link,
                    "years": {"start": None, "end": None},
                }

                # Find the actual <a> tag for this licence in the cell
                licence_text = licence_link.get("text", "")
                licence_url = licence_link.get("url", "")

                licence_tag = None
                for a_tag in cell.find_all("a"):
                    if clean_infobox_text(a_tag.get_text(strip=True)) == licence_text:
                        # Verify URL matches if present
                        # licence_url is a full URL, a_href is relative
                        a_href = a_tag.get("href", "") or ""
                        if not licence_url or a_href in licence_url:
                            # Make sure this is not a file/image link
                            if "/file:" not in a_href.lower():
                                licence_tag = a_tag
                                break

                # Look for the next year span after this licence tag
                if licence_tag and year_spans:
                    # Cache all <a> tags once to avoid repeated find_all calls
                    all_a_tags = cell.find_all("a")

                    # Build a map of licence text -> tag for efficient lookup
                    licence_tag_map = {}
                    for other_link in licence_links:
                        if other_link == licence_link:
                            continue
                        other_text = other_link.get("text", "")
                        if other_text and other_text not in licence_tag_map:
                            for a_tag in all_a_tags:
                                if (
                                    clean_infobox_text(a_tag.get_text(strip=True))
                                    == other_text
                                ):
                                    a_href = a_tag.get("href", "") or ""
                                    if "/file:" not in a_href.lower():
                                        licence_tag_map[other_text] = a_tag
                                        break

                    # Find which year span comes after this licence tag
                    for year_span in year_spans:
                        # Check if this span comes after the licence tag in the document order
                        if self._is_element_before(licence_tag, year_span):
                            # This span is after the licence tag
                            # Check if there's another licence link between them
                            has_licence_between = False
                            for other_tag in licence_tag_map.values():
                                # Check if this other licence is between current licence and year span
                                if self._is_element_before(
                                    licence_tag, other_tag
                                ) and self._is_element_before(other_tag, year_span):
                                    has_licence_between = True
                                    break

                            if not has_licence_between:
                                # This year span belongs to this licence
                                year_text = year_span.get_text(strip=True)
                                licence_entry["years"] = YearParser.parse_licence_years(
                                    year_text
                                )
                                break

                licences.append(licence_entry)

            return licences
        except (TypeError, ValueError) as exc:
            text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
            raise DomainParseError(
                f"Nie udało się sparsować licencji wyścigowej: {text!r}.",
                cause=exc,
            ) from exc

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
