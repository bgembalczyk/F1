import re
from typing import Any
from typing import Dict

from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.sponsorship_liveries.parsers.sponsorship_grand_prix_scope import (
    GrandPrixScopeParser,
)
from scrapers.sponsorship_liveries.parsers.sponsorship_record_text import (
    SponsorshipRecordText,
)


class ColourScopeHandler:
    @staticmethod
    def split_or_colours(colours: Any) -> Any:
        if not isinstance(colours, list):
            return colours
        expanded: list[Any] = []
        for item in colours:
            if not isinstance(item, str):
                expanded.append(item)
                continue
            if re.search(r"\s+or\s+", item, flags=re.IGNORECASE):
                parts = [
                    clean_wiki_text(part)
                    for part in re.split(r"\s+or\s+", item, flags=re.IGNORECASE)
                ]
                expanded.extend([part for part in parts if part])
                continue
            expanded.append(item)
        return expanded

    @staticmethod
    def filter_colours_for_years(colours: Any, years: set[int]) -> Any:
        if not isinstance(colours, list):
            return colours
        filtered: list[Any] = []
        for item in colours:
            if not isinstance(item, str):
                filtered.append(item)
                continue
            year_params = SponsorshipRecordText.extract_years_from_text(item)
            if not year_params:
                filtered.append(item)
                continue
            if year_params & years:
                if re.search(r"grand prix", item, flags=re.IGNORECASE):
                    filtered.append(SponsorshipRecordText.strip_years_keep_context(item))
                else:
                    filtered.append(SponsorshipRecordText.strip_year_suffix(item))
        return filtered

    @staticmethod
    def remove_year_specific_colours(colours: Any) -> Any:
        if not isinstance(colours, list):
            return colours
        filtered: list[Any] = []
        for item in colours:
            if not isinstance(item, str):
                filtered.append(item)
                continue
            if not SponsorshipRecordText.extract_years_from_text(item):
                filtered.append(item)
        return filtered

    @staticmethod
    def filter_colours_for_year(colours: Any, year: int) -> Any:
        if not isinstance(colours, list):
            return colours
        filtered: list[Any] = []
        for item in colours:
            if not isinstance(item, str):
                filtered.append(item)
                continue
            year_params = SponsorshipRecordText.extract_years_from_text(item)
            if not year_params or year in year_params:
                if not year_params:
                    filtered.append(item)
                    continue
                if re.search(r"grand prix", item, flags=re.IGNORECASE):
                    filtered.append(SponsorshipRecordText.strip_years_keep_context(item))
                else:
                    filtered.append(SponsorshipRecordText.strip_year_suffix(item))
        return filtered

    @staticmethod
    def colour_grand_prix_scope(
        colour: str,
    ) -> tuple[dict[str, Any] | None, str]:
        match = re.search(r"\(([^)]*grand prix[^)]*)\)", colour, flags=re.IGNORECASE)
        cleaned_colour = SponsorshipRecordText.strip_year_suffix(colour)
        if not match:
            return None, cleaned_colour
        scope_text = match.group(1)
        scope_text = re.sub(r"\b\d{4}\b", "", scope_text)
        scope_text = re.sub(r"\b\d{3}0s\b", "", scope_text)
        scope_text = clean_wiki_text(scope_text)
        if not scope_text or not re.search(
            r"grand prix", scope_text, flags=re.IGNORECASE
        ):
            return None, cleaned_colour
        names = GrandPrixScopeParser.parse_grand_prix_names(scope_text)
        scope = {
            "type": "only",
            "grand_prix": [{"text": name} for name in names],
        }
        return scope, cleaned_colour

    @staticmethod
    def colour_is_replacement(record: Dict[str, Any], colour: str) -> bool:
        colour_lower = colour.lower()
        pattern = re.compile(
            rf"livery\s+is\s+colou?red\s+{re.escape(colour_lower)}",
            flags=re.IGNORECASE,
        )
        for key, value in record.items():
            if not isinstance(value, str):
                continue
            if pattern.search(value):
                return True
        return False

    @staticmethod
    def record_has_year_specific_colours(
        record: Dict[str, Any], colour_keys: set[str]
    ) -> bool:
        for key in colour_keys:
            colours = record.get(key)
            if not isinstance(colours, list):
                continue
            for item in colours:
                if (
                    isinstance(item, str)
                    and SponsorshipRecordText.extract_years_from_text(item)
                ):
                    return True
        return False
