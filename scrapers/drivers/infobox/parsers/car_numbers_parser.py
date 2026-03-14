"""Helper class for parsing car numbers from infobox cells."""

import re
from typing import Any

from bs4 import Tag

from scrapers.base.errors import DomainParseError
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.drivers.infobox.parsers.year_parser import YearParser


class CarNumbersParser:
    """Handles parsing of car numbers with optional year ranges."""

    @staticmethod
    def parse_car_numbers(cell: Tag) -> list[dict[str, Any]]:
        """Parse car numbers with optional year information.

        Handles formats like:
        - "14" -> [{number: 14, years: {start: None, end: None}}]
        - "No. 23 (2015-2018)" -> [{number: 23, years: {start: 2015, end: 2018}}]
        - "14, 23 (2016)" -> multiple entries

        Args:
            cell: BeautifulSoup Tag representing the cell

        Returns:
            List of dictionaries with 'number' and 'years' keys

        Raises:
            DomainParseError: If parsing fails
        """
        raw_text = cell.get_text("\n", strip=True) or ""
        if not raw_text:
            return []
        normalized = clean_wiki_text(raw_text, strip_lang_suffix=False)
        normalized = re.sub(r"\band\b", ",", normalized, flags=re.IGNORECASE)
        normalized = normalized.replace("/", ",").replace(";", ",")
        entries: list[dict[str, Any]] = []
        pattern = re.compile(
            r"(?<!\d)(?P<prefix>No\.?|#|№)?\s*(?P<number>\d+)\s*(?:\((?P<years>[^)]+)\))?",
            re.IGNORECASE,
        )
        for match in pattern.finditer(normalized):
            prefix = match.group("prefix") or ""
            try:
                number = int(match.group("number"))
            except (TypeError, ValueError) as exc:
                msg = f"Nie udało się sparsować numeru samochodu: {raw_text!r}."
                raise DomainParseError(
                    msg,
                    cause=exc,
                ) from exc
            if number >= 1900 and not prefix:
                continue
            years_text = match.group("years") or ""
            years = (
                YearParser.parse_year_range(years_text)
                if years_text
                else {"start": None, "end": None}
            )
            entries.append({"number": number, "years": years})
        return entries
