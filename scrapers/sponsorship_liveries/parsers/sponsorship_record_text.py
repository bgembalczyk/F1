import re
from typing import Any

from scrapers.base.helpers.text_normalization import clean_wiki_text


class SponsorshipRecordText:
    _year_re = re.compile(r"\b\d{4}\b")

    @classmethod
    def extract_year_params(cls, params: list[Any]) -> set[int]:
        years: set[int] = set()
        for param in params:
            text = None
            if isinstance(param, dict):
                text = param.get("text")
            if text is None:
                text = str(param)
            for match in cls._year_re.findall(text):
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
        if not text or not cls._year_re.search(text):
            return False
        stripped = re.sub(r"[\d\s\-–]", "", text)
        return not stripped

    @staticmethod
    def clean_grand_prix_text(text: str) -> str:
        text = re.sub(r"\b(only|onwards?)\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^\s*from\s+", "", text, flags=re.IGNORECASE)
        return clean_wiki_text(text)

    @classmethod
    def extract_years_from_text(cls, text: str) -> set[int]:
        years = {int(match) for match in cls._year_re.findall(text)}
        for decade in re.findall(r"\b(\d{3})0s\b", text):
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
        cleaned = cls._year_re.sub("", text)
        cleaned = re.sub(r"\b\d{3}0s\b", "", cleaned)
        cleaned = re.sub(r"\(\s*\)", "", cleaned)
        return clean_wiki_text(cleaned)
