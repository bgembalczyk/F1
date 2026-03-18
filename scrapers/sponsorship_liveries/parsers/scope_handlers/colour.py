import re
from typing import Any

from scrapers.base.helpers.text import clean_wiki_text
from scrapers.sponsorship_liveries.helpers.constants import POSSESSIVE_COLOUR_RE
from scrapers.sponsorship_liveries.parsers.grand_prix_scope import GrandPrixScopeParser
from scrapers.sponsorship_liveries.parsers.record_text import SponsorshipRecordText
from scrapers.sponsorship_liveries.parsers.splitters.depth_aware_colour import (
    DepthAwareColourSplitter,
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
            parts = ColourScopeHandler._depth_aware_split_on_and_or(item)
            if len(parts) > 1:
                expanded.extend(
                    [clean_wiki_text(p) for p in parts if clean_wiki_text(p)],
                )
            else:
                expanded.append(item)
        return expanded

    @staticmethod
    def _depth_aware_split_on_and_or(text: str) -> list[str]:
        splitter = DepthAwareColourSplitter(text)
        return splitter.split()

    @staticmethod
    def filter_colours_for_years(colours: Any, years: set[int]) -> Any:
        return ColourScopeHandler._filter_colours_by_year_match(
            colours,
            matcher=lambda year_params: bool(year_params & years),
        )

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
        return ColourScopeHandler._filter_colours_by_year_match(
            colours,
            matcher=lambda year_params: year in year_params,
        )

    @staticmethod
    def _filter_colours_by_year_match(
        colours: Any,
        matcher: Any,
    ) -> Any:
        if not isinstance(colours, list):
            return colours
        filtered: list[Any] = []
        for item in colours:
            filtered_item = ColourScopeHandler._filter_colour_item(item, matcher)
            if filtered_item is not None:
                filtered.append(filtered_item)
        return filtered

    @staticmethod
    def _filter_colour_item(item: Any, matcher: Any) -> Any | None:
        if not isinstance(item, str):
            return item
        year_params = SponsorshipRecordText.extract_years_from_text(item)
        if not year_params:
            return item
        if not matcher(year_params):
            return None
        if re.search(r"grand prix", item, flags=re.IGNORECASE):
            return SponsorshipRecordText.strip_years_keep_context(item)
        return SponsorshipRecordText.strip_year_suffix(item)

    @staticmethod
    def colour_grand_prix_scope(
        colour: str,
    ) -> tuple[dict[str, Any] | None, str]:
        match = re.search(
            r"\(([^)]*grands?\s+prix[^)]*)\)",
            colour,
            flags=re.IGNORECASE,
        )
        cleaned_colour = SponsorshipRecordText.strip_year_suffix(colour)
        if not match:
            return None, cleaned_colour
        scope_text = match.group(1)
        scope_text = re.sub(r"\b\d{4}\b", "", scope_text)
        scope_text = re.sub(r"\b\d{3}0s\b", "", scope_text)
        scope_text = clean_wiki_text(scope_text)
        if not scope_text or not re.search(
            r"grands?\s+prix",
            scope_text,
            flags=re.IGNORECASE,
        ):
            return None, cleaned_colour
        names = GrandPrixScopeParser.parse_grand_prix_names(scope_text)
        scope = {
            "type": "only",
            "grand_prix": [{"text": name} for name in names],
        }
        # Strip the grand-prix parenthetical from the colour name so the
        # returned colour is clean (e.g. "Blue" not "Blue (United States and
        # Mexican Grands Prix)").
        stripped = re.sub(
            r"\s*\([^)]*grands?\s+prix[^)]*\)\s*",
            "",
            cleaned_colour,
            flags=re.IGNORECASE,
        ).strip()
        cleaned_colour = stripped or cleaned_colour
        return scope, cleaned_colour

    @staticmethod
    def colour_is_replacement(record: dict[str, Any], colour: str) -> bool:
        colour_lower = colour.lower()
        pattern = re.compile(
            rf"livery\s+is\s+colou?red\s+{re.escape(colour_lower)}",
            flags=re.IGNORECASE,
        )
        for value in record.values():
            if not isinstance(value, str):
                continue
            if pattern.search(value):
                return True
        return False

    @staticmethod
    def record_has_year_specific_colours(
        record: dict[str, Any],
        colour_keys: set[str],
    ) -> bool:
        for key in colour_keys:
            colours = record.get(key)
            if not isinstance(colours, list):
                continue
            for item in colours:
                if isinstance(
                    item,
                    str,
                ) and SponsorshipRecordText.extract_years_from_text(item):
                    return True
        return False

    @classmethod
    def has_possessive_colour_groups(cls, colours: Any) -> bool:
        """Return True if any item in *colours* is a possessive driver colour group.

        A possessive group looks like ``"Green and White (Pescarolo's car)"``:
        the trailing parenthetical contains a name followed by ``'s``.
        """
        if not isinstance(colours, list):
            return False
        return any(
            isinstance(item, str) and POSSESSIVE_COLOUR_RE.match(item)
            for item in colours
        )

    @classmethod
    def extract_possessive_colour_groups(
        cls,
        colours: Any,
    ) -> list[tuple[str | None, list[str]]]:
        """Parse *colours*, splitting possessive driver groups from plain items.

        Returns a list of ``(driver_name, [colour_strings])`` tuples where
        *driver_name* is ``None`` for non-possessive items.

        Example::

            [
                "Blue",
                "Green and White (Pescarolo's car)",
                "White and Red (Beltoise's car)",
            ]
            →
            [(None, ["Blue"]),
             ("Pescarolo", ["Green", "White"]),
             ("Beltoise",  ["White", "Red"])]
        """
        if not isinstance(colours, list):
            return []
        result: list[tuple[str | None, list[str]]] = []
        for item in colours:
            if not isinstance(item, str):
                result.append((None, [item]))
                continue
            m = POSSESSIVE_COLOUR_RE.match(item)
            if m:
                driver_name = clean_wiki_text(m.group(2).strip())
                colour_text = m.group(1).strip()
                colour_parts = [
                    clean_wiki_text(c)
                    for c in re.split(r"\s+and\s+", colour_text, flags=re.IGNORECASE)
                    if clean_wiki_text(c)
                ]
                result.append((driver_name, colour_parts))
            else:
                result.append((None, [item]))
        return result
