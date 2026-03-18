"""Helper class for parsing numeric values from infobox cells."""

import re

from bs4 import Tag

from models.services.helpers import parse_int_values
from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text_normalization import clean_infobox_text


class NumericParser:
    """Handles parsing of numeric values (integers and floats)."""

    @staticmethod
    def parse_int_cell(cell: Tag) -> int | None:
        """Parse an integer value from a cell.

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            Parsed integer or None if not found

        Raises:
            DomainParseError: If parsing fails
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        match = re.search(r"-?\d+", text.replace(",", ""))
        if not match:
            return None
        try:
            return int(match.group(0))
        except (TypeError, ValueError) as exc:
            msg = f"Nie udało się sparsować liczby całkowitej: {text!r}."
            raise DomainParseError(
                msg,
                cause=exc,
            ) from exc

    @staticmethod
    def parse_float_cell(cell: Tag) -> float | None:
        """Parse a float value from a cell.

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            Parsed float or None if not found

        Raises:
            DomainParseError: If parsing fails
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        match = re.search(r"-?\d+(?:\.\d+)?", text.replace(",", ""))
        if not match:
            return None
        try:
            return float(match.group(0))
        except (TypeError, ValueError) as exc:
            msg = f"Nie udało się sparsować liczby zmiennoprzecinkowej: {text!r}."
            raise DomainParseError(
                msg,
                cause=exc,
            ) from exc

    @staticmethod
    def parse_entries(cell: Tag) -> dict[str, int | None]:
        """Parse entries/starts field.

        Extracts two numeric values: entries and starts.

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            Dictionary with 'entries' and 'starts' keys

        Raises:
            DomainParseError: If parsing fails
        """
        text = clean_infobox_text(cell.get_text(" ", strip=True)) or ""
        try:
            values = parse_int_values(text)
        except (TypeError, ValueError) as exc:
            msg = f"Nie udało się sparsować wpisów/startów: {text!r}."
            raise DomainParseError(
                msg,
                cause=exc,
            ) from exc
        entries = values[0] if values else None
        starts = values[1] if len(values) > 1 else None
        return {"entries": entries, "starts": starts}
