from typing import Any
from typing import Dict
from typing import List

from scrapers.sponsorship_liveries.parsers.colour_scope import (
    ColourScopeHandler,
)
from scrapers.sponsorship_liveries.parsers.grand_prix_scope import (
    GrandPrixScopeParser,
)
from scrapers.sponsorship_liveries.parsers.record_text import (
    SponsorshipRecordText,
)
from scrapers.sponsorship_liveries.parsers.sponsor_scope import (
    SponsorScopeHandler,
)


class SponsorshipRecordSplitter:
    _sponsor_keys = {
        "main_sponsors",
        "additional_major_sponsors",
        "livery_sponsors",
    }
    _colour_keys = {
        "main_colours",
        "additional_colours",
    }

    def split_record_by_season(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        for key in self._colour_keys:
            if key in record:
                record = {
                    **record,
                    key: ColourScopeHandler.split_or_colours(record[key]),
                }
        seasons = record.get("season")
        if not isinstance(seasons, list) or len(seasons) <= 1:
            return self._split_record_by_grand_prix(record)

        if not SponsorScopeHandler.record_has_year_specific_sponsors(
            record, self._sponsor_keys
        ):
            if ColourScopeHandler.record_has_year_specific_colours(
                record, self._colour_keys
            ):
                return self._split_record_by_colour_scopes(record, seasons)
            return self._split_record_by_grand_prix(record)

        season_entries = [
            season
            for season in seasons
            if isinstance(season, dict) and isinstance(season.get("year"), int)
        ]
        if len(season_entries) <= 1:
            return [record]

        split_records: list[Dict[str, Any]] = []
        for season_entry in season_entries:
            year = season_entry["year"]
            new_record = {**record, "season": [season_entry]}
            for key in self._sponsor_keys:
                if key in record:
                    new_record[key] = SponsorScopeHandler.filter_sponsors_for_year(
                        record[key], year
                    )
            for key in self._colour_keys:
                if key in record:
                    new_record[key] = ColourScopeHandler.filter_colours_for_year(
                        record[key], year
                    )
            split_records.extend(self._split_record_by_grand_prix(new_record))
        return split_records

    def _split_record_by_colour_scopes(
        self, record: Dict[str, Any], seasons: list[Any]
    ) -> List[Dict[str, Any]]:
        season_entries = [
            season
            for season in seasons
            if isinstance(season, dict) and isinstance(season.get("year"), int)
        ]
        if len(season_entries) <= 1:
            return [record]

        colour_year_sets: list[set[int]] = []
        for key in self._colour_keys:
            colours = record.get(key)
            if not isinstance(colours, list):
                continue
            for item in colours:
                if not isinstance(item, str):
                    continue
                years = SponsorshipRecordText.extract_years_from_text(item)
                if years:
                    colour_year_sets.append(years)

        if not colour_year_sets:
            return self._split_record_by_grand_prix(record)

        all_years = set().union(*colour_year_sets)
        split_records: list[Dict[str, Any]] = []

        base_seasons = [
            season for season in season_entries if season["year"] not in all_years
        ]
        if base_seasons:
            base_record = {**record, "season": base_seasons}
            for key in self._colour_keys:
                if key in record:
                    base_record[key] = ColourScopeHandler.remove_year_specific_colours(
                        record[key]
                    )
            split_records.extend(self._split_record_by_grand_prix(base_record))

        unique_year_sets: list[set[int]] = []
        for years in colour_year_sets:
            if not any(years == existing for existing in unique_year_sets):
                unique_year_sets.append(years)

        for years in unique_year_sets:
            scoped_seasons = [
                season for season in season_entries if season["year"] in years
            ]
            if not scoped_seasons:
                continue
            scoped_record = {**record, "season": scoped_seasons}
            for key in self._colour_keys:
                if key in record:
                    scoped_record[key] = ColourScopeHandler.filter_colours_for_years(
                        record[key], years
                    )
            split_records.extend(self._split_record_by_grand_prix(scoped_record))

        return split_records

    def _split_record_by_grand_prix(
        self, record: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        scoped_items: dict[str, list[tuple[dict[str, Any], Any]]] = {}
        base_sponsors: dict[str, list[Any]] = {}
        scoped_colours: dict[str, list[tuple[dict[str, Any], str, bool]]] = {}
        base_colours: dict[str, list[Any]] = {}

        for key in self._sponsor_keys:
            sponsors = record.get(key)
            if not isinstance(sponsors, list):
                continue
            base_list: list[Any] = []
            scoped_list: list[tuple[dict[str, Any], Any]] = []
            for item in sponsors:
                if isinstance(item, dict) and item.get("params"):
                    params = item.get("params") or []
                    scope = GrandPrixScopeParser.parse_grand_prix_scope(params)
                    cleaned_item = {k: v for k, v in item.items() if k != "params"}
                    if scope:
                        scoped_list.append((scope, cleaned_item))
                    else:
                        base_list.append(cleaned_item)
                elif isinstance(item, dict) and "params" in item:
                    cleaned_item = {k: v for k, v in item.items() if k != "params"}
                    base_list.append(cleaned_item)
                else:
                    base_list.append(item)
            base_sponsors[key] = base_list
            if scoped_list:
                scoped_items[key] = scoped_list

        for key in self._colour_keys:
            colours = record.get(key)
            if not isinstance(colours, list):
                continue
            base_list: list[Any] = []
            scoped_list: list[tuple[dict[str, Any], str, bool]] = []
            for item in colours:
                if not isinstance(item, str):
                    base_list.append(item)
                    continue
                scope, cleaned = ColourScopeHandler.colour_grand_prix_scope(item)
                if scope:
                    scoped_list.append(
                        (
                            scope,
                            cleaned,
                            ColourScopeHandler.colour_is_replacement(record, cleaned),
                        )
                    )
                else:
                    base_list.append(item)
            base_colours[key] = base_list
            if scoped_list:
                scoped_colours[key] = scoped_list

        if not scoped_items and not scoped_colours:
            return [record]

        scope_map: dict[tuple[Any, ...], dict[str, Any]] = {}
        for key, scoped_list in scoped_items.items():
            for scope, item in scoped_list:
                scope_key = GrandPrixScopeParser.grand_prix_scope_key(scope)
                scope_entry = scope_map.setdefault(
                    scope_key, {"scope": scope, "items": {}}
                )
                scope_entry["items"].setdefault(key, []).append(item)

        for key, scoped_list in scoped_colours.items():
            for scope, colour, replace in scoped_list:
                scope_key = GrandPrixScopeParser.grand_prix_scope_key(scope)
                scope_entry = scope_map.setdefault(
                    scope_key, {"scope": scope, "items": {}}
                )
                scope_entry["items"].setdefault(key, []).append(
                    {"colour": colour, "replace": replace}
                )

        split_records: list[Dict[str, Any]] = []
        for scope_entry in scope_map.values():
            new_record = {**record, "grand_prix_scope": scope_entry["scope"]}
            for key in self._sponsor_keys:
                if key not in base_sponsors:
                    continue
                scoped_list = scope_entry["items"].get(key, [])
                new_record[key] = base_sponsors[key] + scoped_list
            for key in self._colour_keys:
                if key not in base_colours:
                    continue
                scoped_list = scope_entry["items"].get(key, [])
                scoped_colours_list = [item["colour"] for item in scoped_list]
                has_replacement = any(item.get("replace") for item in scoped_list)
                if scoped_colours_list:
                    if has_replacement:
                        new_record[key] = scoped_colours_list
                    else:
                        new_record[key] = base_colours[key] + scoped_colours_list
                else:
                    new_record[key] = base_colours[key]
            split_records.append(new_record)

        other_record = {**record, "grand_prix_scope": {"type": "other"}}
        for key in self._sponsor_keys:
            if key not in base_sponsors:
                continue
            other_record[key] = base_sponsors[key]
        for key in self._colour_keys:
            if key not in base_colours:
                continue
            other_record[key] = base_colours[key]
        split_records.append(other_record)
        return split_records
