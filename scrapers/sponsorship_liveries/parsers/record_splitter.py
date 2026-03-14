from typing import Any

from scrapers.sponsorship_liveries.parsers.colour_scope import ColourScopeHandler
from scrapers.sponsorship_liveries.parsers.grand_prix_scope import GrandPrixScopeParser
from scrapers.sponsorship_liveries.parsers.record_text import SponsorshipRecordText
from scrapers.sponsorship_liveries.parsers.sponsor_scope import SponsorScopeHandler


class SponsorshipRecordSplitter:
    _sponsor_keys = {
        "main_sponsors",
        "additional_major_sponsors",
        "livery_sponsors",
        "livery_principal_sponsors",
    }
    _colour_keys = {
        "main_colours",
        "additional_colours",
    }

    def split_record_by_season(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        for key in self._colour_keys:
            if key in record:
                record = {
                    **record,
                    key: ColourScopeHandler.split_or_colours(record[key]),
                }
        # After split_or_colours, possessive colour groups (e.g. "Green and
        # White (Pescarolo's car)") are kept intact.  Expand them into
        # driver-specific sub-records before any further splitting so that
        # each driver gets their own record with clean colour lists.
        if self._record_has_possessive_colours(record):
            driver_records = self._split_record_by_driver_colours(record)
            result: list[dict[str, Any]] = []
            for dr in driver_records:
                result.extend(self._split_record_by_season_and_gp(dr))
            return result
        return self._split_record_by_season_and_gp(record)

    def _split_record_by_season_and_gp(
        self,
        record: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Continue splitting a record once colour processing is complete."""
        seasons = record.get("season")
        if not isinstance(seasons, list) or len(seasons) <= 1:
            return self._split_record_by_grand_prix(record)

        if not SponsorScopeHandler.record_has_year_specific_sponsors(
            record,
            self._sponsor_keys,
        ):
            if ColourScopeHandler.record_has_year_specific_colours(
                record,
                self._colour_keys,
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

        split_records: list[dict[str, Any]] = []
        for season_entry in season_entries:
            year = season_entry["year"]
            new_record = {**record, "season": [season_entry]}
            for key in self._sponsor_keys:
                if key in record:
                    new_record[key] = SponsorScopeHandler.filter_sponsors_for_year(
                        record[key],
                        year,
                    )
            for key in self._colour_keys:
                if key in record:
                    new_record[key] = ColourScopeHandler.filter_colours_for_year(
                        record[key],
                        year,
                    )
            split_records.extend(self._split_record_by_grand_prix(new_record))
        return split_records

    def _record_has_possessive_colours(self, record: dict[str, Any]) -> bool:
        """Return True when any colour field has a possessive driver group."""
        for key in self._colour_keys:
            if ColourScopeHandler.has_possessive_colour_groups(record.get(key)):
                return True
        return False

    def _split_record_by_driver_colours(
        self,
        record: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Split *record* into one record per driver found in possessive colour groups.

        For each colour key that contains possessive groups (e.g.
        ``["Green and White (Pescarolo's car)", "White and Red (Beltoise's car)"]``):

        * the individual colours for each driver are extracted (``"Green and
          White"`` → ``["Green", "White"]``);
        * non-possessive items in the same field are shared across all driver
          records;
        * colour keys that contain no possessive groups are copied unchanged.

        Each resulting record gains a ``"driver"`` field with a single entry
        ``[{"text": driver_name}]``.
        """
        # driver_name → {colour_key: [colours specific to that driver]}
        driver_colour_map: dict[str, dict[str, list[Any]]] = {}
        # colour_key → [items that are NOT possessive groups (shared)]
        common_by_key: dict[str, list[Any]] = {}

        for key in self._colour_keys:
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
            for key in self._colour_keys:
                if key not in record:
                    continue
                specific = colour_map.get(key, [])
                common = common_by_key.get(key, [])
                new_record[key] = specific + common
            result.append(new_record)
        return result

    def _split_record_by_colour_scopes(  # noqa: C901, PLR0912
        self,
        record: dict[str, Any],
        seasons: list[Any],
    ) -> list[dict[str, Any]]:
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
        split_records: list[dict[str, Any]] = []

        base_seasons = [
            season for season in season_entries if season["year"] not in all_years
        ]
        if base_seasons:
            base_record = {**record, "season": base_seasons}
            for key in self._colour_keys:
                if key in record:
                    base_record[key] = ColourScopeHandler.remove_year_specific_colours(
                        record[key],
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
                        record[key],
                        years,
                    )
            split_records.extend(self._split_record_by_grand_prix(scoped_record))

        return split_records

    def _split_record_by_grand_prix(
        self,
        record: dict[str, Any],
    ) -> list[dict[str, Any]]:
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

    def _separate_sponsors(
        self,
        record: dict[str, Any],
    ) -> tuple[dict[str, list[Any]], dict[str, list[Any]]]:
        """Partition sponsor lists into base and GP-scoped items.

        Args:
            record: The full sponsorship record dict

        Returns:
            Tuple of (base_sponsors, scoped_items) where each value is a dict
            mapping sponsor key to the corresponding item list.
        """
        base_sponsors: dict[str, list[Any]] = {}
        scoped_items: dict[str, list[tuple[dict[str, Any], Any]]] = {}

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

        return base_sponsors, scoped_items

    def _separate_colours(
        self,
        record: dict[str, Any],
    ) -> tuple[dict[str, list[Any]], dict[str, list[Any]]]:
        """Partition colour lists into base and GP-scoped items.

        Args:
            record: The full sponsorship record dict

        Returns:
            Tuple of (base_colours, scoped_colours) where each value is a dict
            mapping colour key to the corresponding item list.
        """
        base_colours: dict[str, list[Any]] = {}
        scoped_colours: dict[str, list[tuple[dict[str, Any], str, bool]]] = {}

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
                        ),
                    )
                else:
                    base_list.append(item)
            base_colours[key] = base_list
            if scoped_list:
                scoped_colours[key] = scoped_list

        return base_colours, scoped_colours

    @staticmethod
    def _build_scope_map(  # noqa: C901, PLR0912
        scoped_items: dict[str, list],
        scoped_colours: dict[str, list],
    ) -> dict[tuple, dict[str, Any]]:
        """Aggregate scoped sponsor and colour items into a keyed scope map.

        ``only`` scopes are expanded to one entry per individual Grand Prix so
        that sponsors whose scopes *overlap* (e.g. A covers {SA, US-W} and B
        covers {US-W, US}) are combined into a single record for the shared GP
        (US-W → A + B) rather than two separate records.  GPs that end up with
        an identical item-set are merged back into a multi-GP ``only`` scope.

        Non-``only`` scopes (range, etc.) are handled with the original
        single-entry behaviour.

        Args:
            scoped_items: Mapping of sponsor key to list of (scope, item) tuples
            scoped_colours: Mapping of colour key to
                list of (scope, colour, replace) tuples

        Returns:
            Dict mapping a stable items-key tuple to a dict with 'scope' and
            'items' entries, where 'items' maps sponsor/colour keys to lists of
            scoped items.
        """
        # gp_key  →  {field_key: [items]}   (individual GP or non-"only" scope key)
        gp_item_map: dict[tuple[Any, ...], dict[str, list[Any]]] = {}
        # gp_key  →  single-GP scope entry used when re-building the final scope
        gp_scope_for_key: dict[tuple[Any, ...], dict[str, Any]] = {}

        def _add(
            gp_key: tuple[Any, ...],
            gp_scope: dict[str, Any],
            field_key: str,
            item: Any,
        ) -> None:
            gp_scope_for_key[gp_key] = gp_scope
            gp_item_map.setdefault(gp_key, {}).setdefault(field_key, []).append(item)

        for key, scoped_list in scoped_items.items():
            for scope, item in scoped_list:
                if scope.get("type") == "only":
                    for gp_entry in scope.get("grand_prix") or []:
                        gp_key = (gp_entry.get("text"), gp_entry.get("url"))
                        _add(
                            gp_key,
                            {"type": "only", "grand_prix": [gp_entry]},
                            key,
                            item,
                        )
                else:
                    scope_key = GrandPrixScopeParser.grand_prix_scope_key(scope)
                    _add(scope_key, scope, key, item)

        for key, scoped_list in scoped_colours.items():
            for scope, colour, replace in scoped_list:
                colour_entry = {"colour": colour, "replace": replace}
                if scope.get("type") == "only":
                    for gp_entry in scope.get("grand_prix") or []:
                        gp_key = (gp_entry.get("text"), gp_entry.get("url"))
                        _add(
                            gp_key,
                            {"type": "only", "grand_prix": [gp_entry]},
                            key,
                            colour_entry,
                        )
                else:
                    scope_key = GrandPrixScopeParser.grand_prix_scope_key(scope)
                    _add(scope_key, scope, key, colour_entry)

        if not gp_item_map:
            return {}

        def _items_key(d: dict[str, list[Any]]) -> tuple[Any, ...]:
            """Produce a stable, hashable fingerprint of an items-dict."""
            parts: list[Any] = []
            for k in sorted(d.keys()):
                for item in d[k]:
                    if isinstance(item, dict):
                        parts.append(
                            (
                                k,
                                tuple(sorted((ki, str(vi)) for ki, vi in item.items())),
                            ),
                        )
                    else:
                        parts.append((k, str(item)))
            return tuple(parts)

        # Group individual-GP keys by the set of items they carry.
        group_to_gps: dict[tuple[Any, ...], list[tuple[Any, ...]]] = {}
        for gp_key, items_dict in gp_item_map.items():
            ik = _items_key(items_dict)
            group_to_gps.setdefault(ik, []).append(gp_key)

        scope_map: dict[tuple[Any, ...], dict[str, Any]] = {}
        for ik, gp_keys in group_to_gps.items():
            items_dict = gp_item_map[gp_keys[0]]
            all_only = all(
                gp_scope_for_key.get(gk, {}).get("type") == "only" for gk in gp_keys
            )
            if all_only:
                gp_entries: list[dict[str, Any]] = []
                for gk in gp_keys:
                    gp_entries.extend(gp_scope_for_key[gk].get("grand_prix", []))
                merged_scope: dict[str, Any] = {
                    "type": "only",
                    "grand_prix": gp_entries,
                }
            else:
                merged_scope = gp_scope_for_key[gp_keys[0]]
            scope_map[ik] = {"scope": merged_scope, "items": items_dict}

        return scope_map

    def _build_split_records(
        self,
        record: dict[str, Any],
        scope_map: dict[tuple, dict[str, Any]],
        base_sponsors: dict[str, list[Any]],
        base_colours: dict[str, list[Any]],
    ) -> list[dict[str, Any]]:
        """Create one record per GP scope, merging base items with scope-specific ones.

        Args:
            record: The original full record
            scope_map: Aggregated scope data from :meth:`_build_scope_map`
            base_sponsors: Base (non-scoped) sponsor lists per key
            base_colours: Base (non-scoped) colour lists per key

        Returns:
            List of new record dicts, one per scope entry.
        """
        split_records: list[dict[str, Any]] = []

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

        return split_records

    def _build_other_record(
        self,
        record: dict[str, Any],
        base_sponsors: dict[str, list[Any]],
        base_colours: dict[str, list[Any]],
    ) -> dict[str, Any]:
        """Build the catch-all "other" record containing only base items.

        Args:
            record: The original full record
            base_sponsors: Base (non-scoped) sponsor lists per key
            base_colours: Base (non-scoped) colour lists per key

        Returns:
            New record dict with grand_prix_scope set to {"type": "other"}.
        """
        other_record = {**record, "grand_prix_scope": {"type": "other"}}
        for key in self._sponsor_keys:
            if key in base_sponsors:
                other_record[key] = base_sponsors[key]
        for key in self._colour_keys:
            if key in base_colours:
                other_record[key] = base_colours[key]
        return other_record
