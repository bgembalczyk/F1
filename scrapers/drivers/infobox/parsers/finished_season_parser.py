"""Helper class for parsing finished season information from infobox cells."""

import re
from typing import Any

from bs4 import Tag

from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text_normalization import clean_infobox_text


class FinishedSeasonParser:
    """Handles parsing of 'Finished last season' field."""

    @staticmethod
    def parse_finished_last_season(cell: Tag) -> dict[str, Any]:
        """Parse 'Finished last season' field.

        Example: "14th (62 pts)" -> {position: "14th", points: 62}

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            Dictionary with 'position' and 'points' keys

        Raises:
            DomainParseError: If parsing fails
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        try:
            result: dict[str, Any] = {"position": None, "points": None}

            # Extract position (before parentheses)
            pos_match = re.match(r"^([^(]+)", text)
            if pos_match:
                result["position"] = pos_match.group(1).strip() or None

            # Extract points from parentheses
            pts_match = re.search(r"\((\d+(?:\.\d+)?)\s*pts?\)", text)
            if pts_match:
                points_str = pts_match.group(1)
                try:
                    # Try parsing as int first
                    result["points"] = int(points_str)
                except ValueError:
                    # Fall back to float
                    result["points"] = float(points_str)

            return result  # noqa: TRY300
        except (TypeError, ValueError) as exc:
            msg = f"Nie udało się sparsować ostatniego sezonu: {text!r}."
            raise DomainParseError(
                msg,
                cause=exc,
            ) from exc
