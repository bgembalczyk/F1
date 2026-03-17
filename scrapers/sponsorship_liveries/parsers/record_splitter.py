from __future__ import annotations

from typing import Any
from typing import Protocol

from scrapers.sponsorship_liveries.parsers.colour_scope import ColourScopeHandler
from scrapers.sponsorship_liveries.parsers.grand_prix_scope import GrandPrixScopeParser
from scrapers.sponsorship_liveries.parsers.record_text import SponsorshipRecordText
from scrapers.sponsorship_liveries.parsers.sponsor_scope import SponsorScopeHandler

SPONSOR_KEYS = {
    "main_sponsors",
    "additional_major_sponsors",
    "livery_sponsors",
    "livery_principal_sponsors",
}
COLOUR_KEYS = {
    "main_colours",
    "additional_colours",
}


class RecordSplitStrategy(Protocol):
    def apply(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        """Split a record into zero, one, or many records."""


class SplitRule(Protocol):
    def should_apply(self, record: dict[str, Any]) -> bool:
        """Return True when a strategy branch should run for this record."""


class HasPossessiveColoursRule:
    def should_apply(self, record: dict[str, Any]) -> bool:
        return any(
            ColourScopeHandler.has_possessive_colour_groups(record.get(key))
            for key in COLOUR_KEYS
        )


class HasMultipleSeasonsRule:
    def should_apply(self, record: dict[str, Any]) -> bool:
        seasons = record.get("season")
        return isinstance(seasons, list) and len(seasons) > 1


class HasYearSpecificSponsorsRule:
    def should_apply(self, record: dict[str, Any]) -> bool:
        return SponsorScopeHandler.record_has_year_specific_sponsors(
            record,
            SPONSOR_KEYS,
        )


class HasYearSpecificColoursRule:
    def should_apply(self, record: dict[str, Any]) -> bool:
        return ColourScopeHandler.record_has_year_specific_colours(record, COLOUR_KEYS)


class PossessiveDriverColourSplitStrategy:
    def __init__(self, rule: SplitRule | None = None):
        self._rule = rule or HasPossessiveColoursRule()

    def apply(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        normalized = self._normalize_colours(record)
        if not self._rule.should_apply(normalized):
            return [normalized]
        return self._split_by_driver_colours(normalized)

    @staticmethod
    def _normalize_colours(record: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(record)
        for key in COLOUR_KEYS:
            if key in normalized:
                normalized[key] = ColourScopeHandler.split_or_colours(normalized[key])
        return normalized

    @staticmethod
    def _split_by_driver_colours(record: dict[str, Any]) -> list[dict[str, Any]]:
        driver_colour_map: dict[str, dict[str, list[Any]]] = {}
        common_by_key: dict[str, list[Any]] = {}

        for key in COLOUR_KEYS:
            colours = record.get(key)
            if not isinstance(colours, list):
                continue
            groups = ColourScopeHandler.extract_possessive_colour_groups(colours)
            common_by_key[key] = []
            for driver_name, colour_list in groups:
                if driver_name is None:
                    common_by_key[key].extend(colour_list)
                else:
                    driver_colour_map.setdefault(driver_name, {}).setdefault(
                        key,
                        [],
                    ).extend(colour_list)

        if not driver_colour_map:
            return [record]

        result: list[dict[str, Any]] = []
        for driver_name, colour_map in driver_colour_map.items():
            new_record: dict[str, Any] = {**record, "driver": [{"text": driver_name}]}
            for key in COLOUR_KEYS:
                if key not in record:
                    continue
                specific = colour_map.get(key, [])
                common = common_by_key.get(key, [])
                new_record[key] = specific + common
            result.append(new_record)
        return result


class SeasonSplitStrategy:
    def __init__(
        self,
        *,
        multiple_seasons_rule: SplitRule | None = None,
        year_sponsors_rule: SplitRule | None = None,
        year_colours_rule: SplitRule | None = None,
    ):
        self._multiple_seasons_rule = multiple_seasons_rule or HasMultipleSeasonsRule()
        self._year_sponsors_rule = year_sponsors_rule or HasYearSpecificSponsorsRule()
        self._year_colours_rule = year_colours_rule or HasYearSpecificColoursRule()

    def apply(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        if not self._multiple_seasons_rule.should_apply(record):
            return [record]

        seasons = record.get("season")
        season_entries = self._season_entries(seasons)
        if len(season_entries) <= 1:
            return [record]

        if not self._year_sponsors_rule.should_apply(record):
            if self._year_colours_rule.should_apply(record):
                return self._split_record_by_colour_scopes(record, season_entries)
            return [record]

        split_records: list[dict[str, Any]] = []
        for season_entry in season_entries:
            year = season_entry["year"]
            new_record = {**record, "season": [season_entry]}
            for key in SPONSOR_KEYS:
                if key in record:
                    new_record[key] = SponsorScopeHandler.filter_sponsors_for_year(
                        record[key],
                        year,
                    )
            for key in COLOUR_KEYS:
                if key in record:
                    new_record[key] = ColourScopeHandler.filter_colours_for_year(
                        record[key],
                        year,
                    )
            split_records.append(new_record)

        return split_records

    @staticmethod
    def _season_entries(seasons: Any) -> list[dict[str, Any]]:
        if not isinstance(seasons, list):
            return []
        return [
            season
            for season in seasons
            if isinstance(season, dict) and isinstance(season.get("year"), int)
        ]

    @staticmethod
    def _split_record_by_colour_scopes(
        record: dict[str, Any],
        season_entries: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        colour_year_sets = SeasonSplitStrategy._extract_colour_year_sets(record)
        if not colour_year_sets:
            return [record]

        split_records = SeasonSplitStrategy._build_base_colour_scoped_records(
            record,
            season_entries,
            colour_year_sets,
        )
        split_records.extend(
            SeasonSplitStrategy._build_year_scoped_colour_records(
                record,
                season_entries,
                colour_year_sets,
            ),
        )
        return split_records

    @staticmethod
    def _extract_colour_year_sets(record: dict[str, Any]) -> list[set[int]]:
        colour_year_sets: list[set[int]] = []
        for key in COLOUR_KEYS:
            colours = record.get(key)
            if not isinstance(colours, list):
                continue
            for item in colours:
                if not isinstance(item, str):
                    continue
                years = SponsorshipRecordText.extract_years_from_text(item)
                if years:
                    colour_year_sets.append(years)
        return colour_year_sets

    @staticmethod
    def _build_base_colour_scoped_records(
        record: dict[str, Any],
        season_entries: list[dict[str, Any]],
        colour_year_sets: list[set[int]],
    ) -> list[dict[str, Any]]:
        all_years = set().union(*colour_year_sets)
        base_seasons = [
            season for season in season_entries if season["year"] not in all_years
        ]
        if not base_seasons:
            return []

        base_record = {**record, "season": base_seasons}
        for key in COLOUR_KEYS:
            if key in record:
                base_record[key] = ColourScopeHandler.remove_year_specific_colours(
                    record[key],
                )
        return [base_record]

    @staticmethod
    def _build_year_scoped_colour_records(
        record: dict[str, Any],
        season_entries: list[dict[str, Any]],
        colour_year_sets: list[set[int]],
    ) -> list[dict[str, Any]]:
        scoped_records: list[dict[str, Any]] = []
        for years in SeasonSplitStrategy._unique_year_sets(colour_year_sets):
            scoped_seasons = [
                season for season in season_entries if season["year"] in years
            ]
            if not scoped_seasons:
                continue
            scoped_record = {**record, "season": scoped_seasons}
            for key in COLOUR_KEYS:
                if key in record:
                    scoped_record[key] = ColourScopeHandler.filter_colours_for_years(
                        record[key],
                        years,
                    )
            scoped_records.append(scoped_record)
        return scoped_records

    @staticmethod
    def _unique_year_sets(year_sets: list[set[int]]) -> list[set[int]]:
        unique_year_sets: list[set[int]] = []
        for years in year_sets:
            if not any(years == existing for existing in unique_year_sets):
                unique_year_sets.append(years)
        return unique_year_sets


class GrandPrixSplitStrategy:
    def apply(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        base_sponsors, scoped_items = self._separate_sponsors(record)
        base_colours, scoped_colours = self._separate_colours(record)

        if not scoped_items and not scoped_colours:
            return [record]

        scope_map = self._build_scope_map(scoped_items, scoped_colours)
        split_records = self._build_split_records(
            record,
            scope_map,
            base_sponsors,
            base_colours,
        )
        split_records.append(
            self._build_other_record(record, base_sponsors, base_colours),
        )
        return split_records

    @staticmethod
    def _separate_sponsors(
        record: dict[str, Any],
    ) -> tuple[dict[str, list[Any]], dict[str, list[Any]]]:
        base_sponsors: dict[str, list[Any]] = {}
        scoped_items: dict[str, list[tuple[dict[str, Any], Any]]] = {}

        for key in SPONSOR_KEYS:
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

        return base_sponsors, scoped_items

    @staticmethod
    def _separate_colours(
        record: dict[str, Any],
    ) -> tuple[dict[str, list[Any]], dict[str, list[Any]]]:
        base_colours: dict[str, list[Any]] = {}
        scoped_colours: dict[str, list[tuple[dict[str, Any], str, bool]]] = {}

        for key in COLOUR_KEYS:
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
                        ),
                    )
                else:
                    base_list.append(item)
            base_colours[key] = base_list
            if scoped_list:
                scoped_colours[key] = scoped_list

        return base_colours, scoped_colours

    @staticmethod
    def _build_scope_map(
        scoped_items: dict[str, list],
        scoped_colours: dict[str, list],
    ) -> dict[tuple, dict[str, Any]]:
        gp_item_map: dict[tuple[Any, ...], dict[str, list[Any]]] = {}
        gp_scope_for_key: dict[tuple[Any, ...], dict[str, Any]] = {}

        GrandPrixSplitStrategy._add_scoped_sponsor_items(
            gp_item_map,
            gp_scope_for_key,
            scoped_items,
        )
        GrandPrixSplitStrategy._add_scoped_colour_items(
            gp_item_map,
            gp_scope_for_key,
            scoped_colours,
        )
        if not gp_item_map:
            return {}

        group_to_gps = GrandPrixSplitStrategy._group_keys_by_items(gp_item_map)
        return GrandPrixSplitStrategy._build_grouped_scope_map(
            gp_item_map,
            gp_scope_for_key,
            group_to_gps,
        )

    @staticmethod
    def _add_scope_item(
        gp_item_map: dict[tuple[Any, ...], dict[str, list[Any]]],
        gp_scope_for_key: dict[tuple[Any, ...], dict[str, Any]],
        gp_key: tuple[Any, ...],
        gp_scope: dict[str, Any],
        field_key: str,
        item: Any,
    ) -> None:
        gp_scope_for_key[gp_key] = gp_scope
        gp_item_map.setdefault(gp_key, {}).setdefault(field_key, []).append(item)

    @staticmethod
    def _scope_keys(
        scope: dict[str, Any],
    ) -> list[tuple[tuple[Any, ...], dict[str, Any]]]:
        if scope.get("type") == "only":
            return [
                (
                    (gp_entry.get("text"), gp_entry.get("url")),
                    {"type": "only", "grand_prix": [gp_entry]},
                )
                for gp_entry in scope.get("grand_prix") or []
            ]
        scope_key = GrandPrixScopeParser.grand_prix_scope_key(scope)
        return [(scope_key, scope)]

    @staticmethod
    def _add_scoped_sponsor_items(
        gp_item_map: dict[tuple[Any, ...], dict[str, list[Any]]],
        gp_scope_for_key: dict[tuple[Any, ...], dict[str, Any]],
        scoped_items: dict[str, list],
    ) -> None:
        for key, scoped_list in scoped_items.items():
            for scope, item in scoped_list:
                for gp_key, gp_scope in GrandPrixSplitStrategy._scope_keys(scope):
                    GrandPrixSplitStrategy._add_scope_item(
                        gp_item_map,
                        gp_scope_for_key,
                        gp_key,
                        gp_scope,
                        key,
                        item,
                    )

    @staticmethod
    def _add_scoped_colour_items(
        gp_item_map: dict[tuple[Any, ...], dict[str, list[Any]]],
        gp_scope_for_key: dict[tuple[Any, ...], dict[str, Any]],
        scoped_colours: dict[str, list],
    ) -> None:
        for key, scoped_list in scoped_colours.items():
            for scope, colour, replace in scoped_list:
                colour_entry = {"colour": colour, "replace": replace}
                for gp_key, gp_scope in GrandPrixSplitStrategy._scope_keys(scope):
                    GrandPrixSplitStrategy._add_scope_item(
                        gp_item_map,
                        gp_scope_for_key,
                        gp_key,
                        gp_scope,
                        key,
                        colour_entry,
                    )

    @staticmethod
    def _items_key(items: dict[str, list[Any]]) -> tuple[Any, ...]:
        parts: list[Any] = []
        for key in sorted(items.keys()):
            for item in items[key]:
                if isinstance(item, dict):
                    parts.append(
                        (
                            key,
                            tuple(
                                sorted(
                                    (item_key, str(value))
                                    for item_key, value in item.items()
                                ),
                            ),
                        ),
                    )
                else:
                    parts.append((key, str(item)))
        return tuple(parts)

    @staticmethod
    def _group_keys_by_items(
        gp_item_map: dict[tuple[Any, ...], dict[str, list[Any]]],
    ) -> dict[tuple[Any, ...], list[tuple[Any, ...]]]:
        grouped: dict[tuple[Any, ...], list[tuple[Any, ...]]] = {}
        for gp_key, items_dict in gp_item_map.items():
            grouped.setdefault(
                GrandPrixSplitStrategy._items_key(items_dict),
                [],
            ).append(gp_key)
        return grouped

    @staticmethod
    def _build_grouped_scope_map(
        gp_item_map: dict[tuple[Any, ...], dict[str, list[Any]]],
        gp_scope_for_key: dict[tuple[Any, ...], dict[str, Any]],
        group_to_gps: dict[tuple[Any, ...], list[tuple[Any, ...]]],
    ) -> dict[tuple[Any, ...], dict[str, Any]]:
        scope_map: dict[tuple[Any, ...], dict[str, Any]] = {}
        for items_key, gp_keys in group_to_gps.items():
            items_dict = gp_item_map[gp_keys[0]]
            merged_scope = GrandPrixSplitStrategy._merge_group_scope(
                gp_scope_for_key,
                gp_keys,
            )
            scope_map[items_key] = {"scope": merged_scope, "items": items_dict}
        return scope_map

    @staticmethod
    def _merge_group_scope(
        gp_scope_for_key: dict[tuple[Any, ...], dict[str, Any]],
        gp_keys: list[tuple[Any, ...]],
    ) -> dict[str, Any]:
        all_only = all(
            gp_scope_for_key.get(gp_key, {}).get("type") == "only" for gp_key in gp_keys
        )
        if not all_only:
            return gp_scope_for_key[gp_keys[0]]

        gp_entries: list[dict[str, Any]] = []
        for gp_key in gp_keys:
            gp_entries.extend(gp_scope_for_key[gp_key].get("grand_prix", []))
        return {"type": "only", "grand_prix": gp_entries}

    @staticmethod
    def _build_split_records(
        record: dict[str, Any],
        scope_map: dict[tuple, dict[str, Any]],
        base_sponsors: dict[str, list[Any]],
        base_colours: dict[str, list[Any]],
    ) -> list[dict[str, Any]]:
        split_records: list[dict[str, Any]] = []

        for scope_entry in scope_map.values():
            new_record = {**record, "grand_prix_scope": scope_entry["scope"]}
            for key in SPONSOR_KEYS:
                if key not in base_sponsors:
                    continue
                scoped_list = scope_entry["items"].get(key, [])
                new_record[key] = base_sponsors[key] + scoped_list
            for key in COLOUR_KEYS:
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

        return split_records

    @staticmethod
    def _build_other_record(
        record: dict[str, Any],
        base_sponsors: dict[str, list[Any]],
        base_colours: dict[str, list[Any]],
    ) -> dict[str, Any]:
        other_record = {**record, "grand_prix_scope": {"type": "other"}}
        for key in SPONSOR_KEYS:
            if key in base_sponsors:
                other_record[key] = base_sponsors[key]
        for key in COLOUR_KEYS:
            if key in base_colours:
                other_record[key] = base_colours[key]
        return other_record


class DeduplicateRecordStrategy:
    def __init__(self):
        self._seen: set[tuple[Any, ...]] = set()

    def reset(self) -> None:
        self._seen.clear()

    def apply(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        fingerprint = self._fingerprint(record)
        if fingerprint in self._seen:
            return []
        self._seen.add(fingerprint)
        return [record]

    @staticmethod
    def _fingerprint(value: Any) -> tuple[Any, ...]:
        if isinstance(value, dict):
            return (
                "dict",
                tuple(
                    (key, DeduplicateRecordStrategy._fingerprint(val))
                    for key, val in sorted(value.items())
                ),
            )
        if isinstance(value, list):
            return (
                "list",
                tuple(DeduplicateRecordStrategy._fingerprint(item) for item in value),
            )
        return ("scalar", str(value))


class RecordSplitPipeline:
    def __init__(self, strategies: list[RecordSplitStrategy]):
        self._strategies = strategies

    def apply(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        for strategy in self._strategies:
            if hasattr(strategy, "reset"):
                strategy.reset()  # type: ignore[attr-defined]

        records = [record]
        for strategy in self._strategies:
            next_records: list[dict[str, Any]] = []
            for candidate in records:
                next_records.extend(strategy.apply(candidate))
            records = next_records
        return records


class SponsorshipRecordSplitter:
    """Facade composing record split strategies in deterministic order."""

    def __init__(self, pipeline: RecordSplitPipeline | None = None):
        self._pipeline = pipeline or RecordSplitPipeline(
            [
                PossessiveDriverColourSplitStrategy(),
                SeasonSplitStrategy(),
                GrandPrixSplitStrategy(),
                DeduplicateRecordStrategy(),
            ],
        )

    def split_record_by_season(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        return self._pipeline.apply(record)
