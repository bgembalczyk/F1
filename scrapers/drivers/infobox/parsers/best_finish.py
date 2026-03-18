"""Helper class for parsing best finish information."""

import re
from typing import Any

from bs4 import Tag

from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text_normalization import clean_infobox_text
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor
from scrapers.drivers.infobox.parsers.season import SeasonParser


class BestFinishParser:
    """Handles parsing of best finish information."""

    def __init__(self, link_extractor: InfoboxLinkExtractor):
        """Initialize the best finish parser.

        Args:
            link_extractor: Link extractor for extracting URLs from cells
        """
        self._link_extractor = link_extractor
        self._season_parser = SeasonParser()

    def parse_best_finish(self, cell: Tag) -> dict[str, Any]:
        """Parse best finish field.

        Extracts result position and associated seasons with optional class information.
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        try:
            result: dict[str, Any] = {"result": None, "seasons": None}

            # Extract result position
            result["result"] = self._extract_result_position(text)

            # Extract season links and class information
            links = self._link_extractor.extract_links(cell)
            season_links = [
                link for link in links if not self._season_parser.is_class_link(link)
            ]

            if season_links:
                small_tags = cell.find_all("small")
                if small_tags:
                    result["seasons"] = self._parse_seasons_with_classes(
                        cell,
                        season_links,
                        small_tags,
                    )
                else:
                    # No small tags, just return seasons
                    result["seasons"] = [
                        {"text": link.get("text", ""), "url": link.get("url")}
                        for link in season_links
                    ]
            else:
                # No links - try to extract years from text
                result["seasons"] = self._extract_seasons_from_text(text)

            return result
        except (TypeError, ValueError) as exc:
            msg = f"Nie udało się sparsować najlepszego wyniku: {text!r}."
            raise DomainParseError(
                msg,
                cause=exc,
            ) from exc

    def _extract_result_position(self, text: str) -> str | None:
        """Extract result position from text."""
        if " in " in text:
            result_text, _ = text.split(" in ", 1)
            return result_text.strip() or None
        # Extract result without parentheses content
        result_match = re.match(r"^([^(]+)", text)
        if result_match:
            return result_match.group(1).strip() or None
        return text.strip() or None

    def _parse_seasons_with_classes(
        self,
        cell: Tag,
        season_links: list[dict[str, Any]],
        small_tags: list[Tag],
    ) -> list[dict[str, Any]]:
        """Parse seasons with class information from small tags."""
        num_small_tags = len(small_tags)

        if num_small_tags == 1:
            return self._parse_single_class_for_all_seasons(
                season_links,
                small_tags[0],
            )
        return self._parse_class_per_season(cell, season_links)

    def _parse_single_class_for_all_seasons(
        self,
        season_links: list[dict[str, Any]],
        small_tag: Tag,
    ) -> list[dict[str, Any]]:
        """Parse case where a single class applies to all seasons."""
        class_links = self._link_extractor.extract_links(small_tag)
        class_info = class_links[0] if class_links else None

        # Validate that class_info is actually a class, not season data
        if not self._season_parser.is_valid_class_info(class_info, season_links):
            class_info = None

        season_data = []
        for season_link in season_links:
            season_entry = {
                "text": season_link.get("text", ""),
                "url": season_link.get("url"),
            }
            if class_info:
                season_entry["class"] = class_info
            season_data.append(season_entry)

        return season_data

    def _parse_class_per_season(
        self,
        cell: Tag,
        season_links: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Parse case where each season may have its own class."""
        season_data = []

        for season_link in season_links:
            season_entry = {
                "text": season_link.get("text", ""),
                "url": season_link.get("url"),
            }

            # Find the actual <a> tag in the cell that matches this season
            season_tag = self._find_season_tag(cell, season_link)

            # Look for next <small> tag after this season tag
            if season_tag:
                class_info = self._find_class_for_season(
                    season_tag,
                    season_link,
                    season_links,
                )
                if class_info:
                    season_entry["class"] = class_info

            season_data.append(season_entry)

        return season_data

    def _find_season_tag(
        self,
        cell: Tag,
        season_link: dict[str, Any],
    ) -> Tag | None:
        """Find the <a> tag for a season link in the cell."""
        season_text = season_link.get("text", "")
        season_url = season_link.get("url", "")

        if not season_text:
            return None

        for a_tag in cell.find_all("a"):
            if clean_infobox_text(a_tag.get_text(strip=True)) == season_text:
                # Verify URL matches if present
                a_href = a_tag.get("href", "") or ""
                if not season_url or a_href in season_url:
                    return a_tag

        return None

    def _find_class_for_season(
        self,
        season_tag: Tag,
        season_link: dict[str, Any],
        season_links: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """Find class information for a specific season."""
        found_small = self._find_nearest_small_tag(
            season_tag,
            season_link,
            season_links,
        )
        if not found_small:
            return None
        return self._extract_valid_class_candidate(found_small, season_link)

    def _find_nearest_small_tag(
        self,
        season_tag: Tag,
        season_link: dict[str, Any],
        season_links: list[dict[str, Any]],
    ) -> Tag | None:
        next_elem = season_tag
        while next_elem:
            next_elem = next_elem.next_sibling
            if next_elem is None:
                return None
            if self._is_other_season_tag(next_elem, season_link, season_links):
                return None
            small_in_elem = self._small_tag_from_elem(
                next_elem,
                season_link,
                season_links,
            )
            if small_in_elem is not None:
                return small_in_elem
        return None

    def _is_other_season_tag(
        self,
        elem: Any,
        season_link: dict[str, Any],
        season_links: list[dict[str, Any]],
    ) -> bool:
        if not isinstance(elem, Tag) or elem.name != "a":
            return False
        next_text = clean_infobox_text(elem.get_text(strip=True))
        return any(s.get("text") == next_text for s in season_links if s != season_link)

    def _small_tag_from_elem(
        self,
        elem: Any,
        season_link: dict[str, Any],
        season_links: list[dict[str, Any]],
    ) -> Tag | None:
        if not isinstance(elem, Tag):
            return None
        if elem.name == "small":
            return elem

        small_in_sibling = elem.find("small")
        if not small_in_sibling:
            return None
        if self._contains_other_season(elem, season_link, season_links):
            return None
        return small_in_sibling

    def _contains_other_season(
        self,
        elem: Tag,
        season_link: dict[str, Any],
        season_links: list[dict[str, Any]],
    ) -> bool:
        for a_tag in elem.find_all("a"):
            a_text = clean_infobox_text(a_tag.get_text(strip=True))
            if any(s.get("text") == a_text for s in season_links if s != season_link):
                return True
        return False

    def _extract_valid_class_candidate(
        self,
        small_tag: Tag,
        season_link: dict[str, Any],
    ) -> dict[str, Any] | None:
        class_links = self._link_extractor.extract_links(small_tag)
        if not class_links:
            return None

        class_candidate = class_links[0]
        class_text = class_candidate.get("text", "")
        class_url = class_candidate.get("url", "")
        season_text = season_link.get("text", "")
        season_url = season_link.get("url", "")

        is_valid = not self._season_parser.is_season_like_text(class_text)
        if is_valid and (season_text == class_text or season_url == class_url):
            is_valid = False
        return class_candidate if is_valid else None

    def _extract_seasons_from_text(self, text: str) -> list[int] | None:
        """Extract seasons from text when no links are available."""
        # Pattern 1: "1st in 1957" -> extract years after "in"
        # Pattern 2: "1st in 1952, 1954" -> extract comma-separated years
        if " in " in text:
            # Extract text after "in"
            _, years_text = text.split(" in ", 1)
            # Remove any parenthetical content
            years_text = re.sub(r"\s*\([^)]*\)", "", years_text).strip()
            # Extract all years from the text
            years = [int(y) for y in re.findall(r"\b(\d{4})\b", years_text)]
            if years:
                return years
        else:
            # Try to find years in parentheses
            paren_match = re.search(r"\(([^)]+)\)", text)
            if paren_match:
                paren_content = paren_match.group(1)
                # Extract all years
                years = [int(y) for y in re.findall(r"\b(\d{4})\b", paren_content)]
                if years:
                    return years

        return None
