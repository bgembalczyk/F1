import re
from typing import Any

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.sponsorship_liveries.helpers.constants import decade_re
from scrapers.sponsorship_liveries.helpers.constants import year_range_abbrev_re
from scrapers.sponsorship_liveries.helpers.constants import year_range_re
from scrapers.sponsorship_liveries.helpers.constants import year_re


class SponsorshipRecordText:
    @classmethod
    def _expand_year_range(cls, start_year: int, end_year: int) -> set[int]:
        if start_year <= end_year:
            return set(range(start_year, end_year + 1))
        return set()

    @classmethod
    def _abbrev_end_year(cls, start_year: int, abbrev: int) -> int:
        """Expand a 2-digit abbreviated end year relative to *start_year*.

        For example: start_year=1979, abbrev=83 → 1983.
        If the abbreviated value is less than the last two digits of
        *start_year*, the next century is used (e.g. start=1999, abbrev=03
        → 2003).
        """
        century = (start_year // 100) * 100
        end_year = century + abbrev
        if end_year < start_year:
            end_year += 100
        return end_year

    @classmethod
    def extract_year_params(cls, params: list[Any]) -> set[int]:
        years: set[int] = set()
        for param in params:
            text = None
            if isinstance(param, dict):
                text = param.get("text")
            if text is None:
                text = str(param)
            # Expand full year ranges like "2021-2023".
            for range_match in year_range_re.finditer(text):
                start_year = int(range_match.group(1))
                end_year = int(range_match.group(2))
                years |= cls._expand_year_range(start_year, end_year)
            # Expand abbreviated end-year ranges like "1979-83".
            # _year_range_abbrev_re and _year_range_re are mutually exclusive:
            # the former requires the end token to be exactly 2 digits (not
            # followed by another digit), so "1979-1983" is only matched by
            # the full-range pattern above.
            for range_match in year_range_abbrev_re.finditer(text):
                start_year = int(range_match.group(1))
                abbrev = int(range_match.group(2))
                end_year = cls._abbrev_end_year(start_year, abbrev)
                years |= cls._expand_year_range(start_year, end_year)
            # Also extract standalone years; set deduplication handles any overlap.
            for match in year_re.findall(text):
                years.add(int(match))
        return years

    @staticmethod
    def param_text(param: Any) -> str:
        if isinstance(param, dict):
            return str(param.get("text") or "")
        return str(param or "")

    @classmethod
    def is_year_param(cls, param: Any) -> bool:
        text = cls.param_text(param)
        if not text or not year_re.search(text):
            return False
        stripped = re.sub(r"[\d\s\--]", "", text)
        return not stripped

    @staticmethod
    def clean_grand_prix_text(text: str) -> str:
        text = re.sub(r"\b(only|onwards?)\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^\s*from\s+", "", text, flags=re.IGNORECASE)
        return clean_wiki_text(text)

    @classmethod
    def extract_years_from_text(cls, text: str) -> set[int]:
        years = {int(match) for match in year_re.findall(text)}
        for decade in decade_re.findall(text):
            start = int(decade) * 10
            years.update(range(start, start + 10))
        return years

    @classmethod
    def strip_year_suffix(cls, text: str) -> str:
        cleaned = re.sub(
            r"\s*\([^)]*\b(\d{4}|\d{3}0s)\b[^)]*\)\s*$",
            "",
            text,
        ).strip()
        if cleaned and cleaned != text:
            return cleaned
        cleaned = re.sub(r"\s*\b(\d{4}|\d{3}0s)\b\s*$", "", text).strip()
        return cleaned or text

    @classmethod
    def strip_years_keep_context(cls, text: str) -> str:
        cleaned = year_re.sub("", text)
        cleaned = decade_re.sub("", cleaned)
        cleaned = re.sub(r"\(\s*\)", "", cleaned)
        return clean_wiki_text(cleaned)
