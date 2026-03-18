from typing import Any

from scrapers.sponsorship_liveries.helpers.constants import COLOUR_KEYS
from scrapers.sponsorship_liveries.helpers.constants import SPONSOR_KEYS
from scrapers.sponsorship_liveries.parsers.grand_prix_scope import GrandPrixScopeParser
from scrapers.sponsorship_liveries.parsers.scope_handlers.colour import ColourScopeHandler


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
            base_list, scoped_list = GrandPrixSplitStrategy._split_sponsor_items(
                sponsors,
            )
            base_sponsors[key] = base_list
            if scoped_list:
                scoped_items[key] = scoped_list

        return base_sponsors, scoped_items

    @staticmethod
    def _split_sponsor_items(
        sponsors: list[Any],
    ) -> tuple[list[Any], list[tuple[dict[str, Any], Any]]]:
        base_list: list[Any] = []
        scoped_list: list[tuple[dict[str, Any], Any]] = []
        for item in sponsors:
            scope_item = GrandPrixSplitStrategy._sponsor_scope_item(item)
            if scope_item is None:
                base_list.append(item)
                continue
            scope, cleaned_item = scope_item
            if scope:
                scoped_list.append((scope, cleaned_item))
            else:
                base_list.append(cleaned_item)
        return base_list, scoped_list

    @staticmethod
    def _sponsor_scope_item(item: Any) -> tuple[dict[str, Any] | None, Any] | None:
        if not isinstance(item, dict) or "params" not in item:
            return None
        params = item.get("params") or []
        scope = GrandPrixScopeParser.parse_grand_prix_scope(params)
        cleaned_item = {k: v for k, v in item.items() if k != "params"}
        return scope, cleaned_item

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
            base_list, scoped_list = GrandPrixSplitStrategy._split_colour_items(
                record,
                colours,
            )
            base_colours[key] = base_list
            if scoped_list:
                scoped_colours[key] = scoped_list

        return base_colours, scoped_colours

    @staticmethod
    def _split_colour_items(
        record: dict[str, Any],
        colours: list[Any],
    ) -> tuple[list[Any], list[tuple[dict[str, Any], str, bool]]]:
        base_list: list[Any] = []
        scoped_list: list[tuple[dict[str, Any], str, bool]] = []
        for item in colours:
            scoped_item = GrandPrixSplitStrategy._colour_scope_item(record, item)
            if scoped_item is None:
                base_list.append(item)
                continue
            scoped_list.append(scoped_item)
        return base_list, scoped_list

    @staticmethod
    def _colour_scope_item(
        record: dict[str, Any],
        item: Any,
    ) -> tuple[dict[str, Any], str, bool] | None:
        if not isinstance(item, str):
            return None
        scope, cleaned = ColourScopeHandler.colour_grand_prix_scope(item)
        if not scope:
            return None
        return (
            scope,
            cleaned,
            ColourScopeHandler.colour_is_replacement(record, cleaned),
        )

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
            GrandPrixSplitStrategy._merge_sponsors(
                new_record,
                scope_entry,
                base_sponsors,
            )
            GrandPrixSplitStrategy._merge_colours(new_record, scope_entry, base_colours)
            split_records.append(new_record)

        return split_records

    @staticmethod
    def _merge_sponsors(
        new_record: dict[str, Any],
        scope_entry: dict[str, Any],
        base_sponsors: dict[str, list[Any]],
    ) -> None:
        for key in SPONSOR_KEYS:
            if key not in base_sponsors:
                continue
            scoped_list = scope_entry["items"].get(key, [])
            new_record[key] = base_sponsors[key] + scoped_list

    @staticmethod
    def _merge_colours(
        new_record: dict[str, Any],
        scope_entry: dict[str, Any],
        base_colours: dict[str, list[Any]],
    ) -> None:
        for key in COLOUR_KEYS:
            if key not in base_colours:
                continue
            scoped_list = scope_entry["items"].get(key, [])
            new_record[key] = GrandPrixSplitStrategy._merged_colour_values(
                base_colours[key],
                scoped_list,
            )

    @staticmethod
    def _merged_colour_values(
        base_colours: list[Any],
        scoped_list: list[dict[str, Any]],
    ) -> list[Any]:
        scoped_colours_list = [item["colour"] for item in scoped_list]
        has_replacement = any(item.get("replace") for item in scoped_list)
        if not scoped_colours_list:
            return base_colours
        if has_replacement:
            return scoped_colours_list
        return base_colours + scoped_colours_list

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


