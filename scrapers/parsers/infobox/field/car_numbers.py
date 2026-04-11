"""Helper class for parsing car numbers from infobox cells."""

import re
from typing import Any

from bs4 import Tag

from scrapers.error_handler import ErrorHandler
from scrapers.helpers.text import clean_wiki_text
from scrapers.parsers.infobox.constants import CAR_NUMBER_PATTERN_RE
from scrapers.parsers.infobox.constants import MIN_VALID_CAR_NUMBER_YEAR
from scrapers.parsers.infobox.constants import MIN_YEAR_TOKENS_FOR_RANGE
from scrapers.parsers.infobox.constants import YEAR_TOKEN_RE
from scrapers.parsers.infobox.field.base import BaseInfoboxFieldParser
from scrapers.parsers.infobox.field.year import YearParser


class CarNumbersParser(BaseInfoboxFieldParser):
    """Handles parsing of car numbers with optional year ranges."""

    def parse(self, cell: Tag) -> list[dict[str, Any]]:
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
        for match in CAR_NUMBER_PATTERN_RE.finditer(normalized):
            prefix = match.group("prefix") or ""
            number = ErrorHandler.run_domain_parse(
                lambda current_match=match: int(current_match.group("number")),
                message=f"Nie udało się sparsować numeru samochodu: {raw_text!r}.",
                parser_name=CarNumbersParser.__name__,
            )
            if number >= MIN_VALID_CAR_NUMBER_YEAR and not prefix:
                continue
            years_text = match.group("years") or ""
            years = {"start": None, "end": None}
            if years_text:
                parsed = YearParser.parse_year_range(years_text)
                year_tokens = YEAR_TOKEN_RE.findall(years_text)
                if len(year_tokens) >= MIN_YEAR_TOKENS_FOR_RANGE:
                    parsed["start"] = int(year_tokens[0])
                    parsed["end"] = int(year_tokens[-1])
                years = parsed
            entries.append({"number": number, "years": years})
        return entries


__all__ = [
    "CarNumbersParser",
]
