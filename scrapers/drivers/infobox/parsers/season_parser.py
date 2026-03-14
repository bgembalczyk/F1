"""Helper class for season-related parsing logic."""

import re
from typing import Any

from models.records.link import LinkRecord


class SeasonParser:
    """Handles parsing and validation of season-related information."""

    # Regex patterns for year detection (compiled once for performance)
    _FOUR_DIGIT_YEAR_PATTERN = re.compile(r"^(19|20)\d{2}$")
    _TWO_DIGIT_SUFFIX_PATTERN = re.compile(r"^\d{2}$")

    def is_class_link(self, link: LinkRecord) -> bool:
        """Check if link is a class designation (e.g., LMP1) rather than a season."""
        url = (link.get("url") or "").lower()
        text = (link.get("text") or "").upper()
        # Class links typically don't contain years or season references
        if "season" in url or "_season" in url:
            return False
        return not re.search(r"\d{4}", text)

    def is_valid_class_info(
        self,
        class_info: dict[str, Any],
        season_links: list[dict[str, Any]],
    ) -> bool:
        """Check if class_info is valid (not season data and not a duplicate).

        Args:
            class_info: The potential class information to validate
            season_links: List of season links to check for duplicates

        Returns:
            True if class_info is a valid class, False if it's season data or a duplicate
        """
        if not class_info:
            return False

        class_text = class_info.get("text", "")
        class_url = class_info.get("url", "")

        # Check if class looks like season data (years only)
        if self.is_season_like_text(class_text):
            return False

        # Check if class duplicates any season
        for season_link in season_links:
            if (
                season_link.get("text") == class_text
                or season_link.get("url") == class_url
            ):
                return False

        return True

    def is_season_like_text(self, text: str) -> bool:
        """Check if text looks like season data (years) rather than a class name.

        Season-like text contains only years and separators:
        - Single years: "2013", "2014"
        - Year ranges with 2-digit suffix: "2013-14", "2019–20" (where "14" means 2014, "20" means 2020)
        - Full year ranges: "2013-2014", "2013–2014"
        - Multiple years: "2013, 2014, 2015"
        - Combinations: "2013-2015, 2018"

        Class names typically contain letters (possibly with numbers) in non-year format.
        Examples of class names: "LMP1", "LMH", "LMP2", "GT3", "LMP2-H"

        Args:
            text: The text to check

        Returns:
            True if the text looks like season/year data, False if it looks like a class name
        """
        if not text:
            return False

        # Remove common separators and whitespace to get individual parts
        cleaned = text.replace(",", " ").replace("–", " ").replace("-", " ")
        parts = cleaned.split()

        if not parts:
            return False

        # Check if all parts are either 4-digit years or 2-digit year suffixes
        # and ensure at least one 4-digit year is present
        has_four_digit_year = False

        for part in parts:
            part = part.strip()
            if not part:
                continue

            if self._FOUR_DIGIT_YEAR_PATTERN.match(part):
                # It's a 4-digit year (1900-2099)
                has_four_digit_year = True
            elif self._TWO_DIGIT_SUFFIX_PATTERN.match(part):
                # It's a 2-digit suffix (00-99)
                # These are only valid when combined with 4-digit years (like "2019-20")
                pass
            else:
                # Not a year or suffix - likely a class name with letters
                return False

        # Valid season-like text must have at least one 4-digit year
        # 2-digit suffixes alone (like "20") are not sufficient
        return has_four_digit_year
