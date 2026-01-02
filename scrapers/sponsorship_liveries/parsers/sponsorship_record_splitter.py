import re
from typing import Any
from typing import Dict
from typing import List

from scrapers.base.helpers.text_normalization import clean_wiki_text


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
    _year_re = re.compile(r"\b\d{4}\b")

    @staticmethod
    def _extract_year_params(params: list[Any]) -> set[int]:
        years: set[int] = set()
        for param in params:
            text = None
            if isinstance(param, dict):
                text = param.get("text")
            if text is None:
                text = str(param)
            for match in SponsorshipRecordSplitter._year_re.findall(text):
                years.add(int(match))
        return years

    @staticmethod
    def _param_text(param: Any) -> str:
        if isinstance(param, dict):
            return str(param.get("text") or "")
        return str(param or "")

    @staticmethod
    def _is_year_param(param: Any) -> bool:
        text = SponsorshipRecordSplitter._param_text(param)
        if not text or not re.search(r"\b\d{4}\b", text):
            return False
        stripped = re.sub(r"[\d\s\-–]", "", text)
        return not stripped

    @staticmethod
    def _clean_grand_prix_text(text: str) -> str:
        text = re.sub(r"\b(only|onwards?)\b", "", text, flags=re.IGNORECASE)
        text = re.sub(r"^\s*from\s+", "", text, flags=re.IGNORECASE)
        return clean_wiki_text(text)

    @staticmethod
    def _extract_years_from_text(text: str) -> set[int]:
        years = {
            int(match) for match in SponsorshipRecordSplitter._year_re.findall(text)
        }
        for decade in re.findall(r"\b(\d{3})0s\b", text):
            start = int(decade) * 10
            years.update(range(start, start + 10))
        return years

    @staticmethod
    def _strip_year_suffix(text: str) -> str:
        cleaned = re.sub(
            r"\s*\([^)]*\b(\d{4}|\d{3}0s)\b[^)]*\)\s*$",
            "",
            text,
        ).strip()
        if cleaned and cleaned != text:
            return cleaned
        cleaned = re.sub(r"\s*\b(\d{4}|\d{3}0s)\b\s*$", "", text).strip()
        return cleaned or text

    @staticmethod
    def _strip_years_keep_context(text: str) -> str:
        cleaned = re.sub(r"\b\d{4}\b", "", text)
        cleaned = re.sub(r"\b\d{3}0s\b", "", cleaned)
        cleaned = re.sub(r"\(\s*\)", "", cleaned)
        return clean_wiki_text(cleaned)

    def _filter_colours_for_years(self, colours: Any, years: set[int]) -> Any:
        if not isinstance(colours, list):
            return colours
        filtered: list[Any] = []
        for item in colours:
            if not isinstance(item, str):
                filtered.append(item)
                continue
            year_params = self._extract_years_from_text(item)
            if not year_params:
                filtered.append(item)
                continue
            if year_params & years:
                if re.search(r"grand prix", item, flags=re.IGNORECASE):
                    filtered.append(self._strip_years_keep_context(item))
                else:
                    filtered.append(self._strip_year_suffix(item))
        return filtered

    def _remove_year_specific_colours(self, colours: Any) -> Any:
        if not isinstance(colours, list):
            return colours
        filtered: list[Any] = []
        for item in colours:
            if not isinstance(item, str):
                filtered.append(item)
                continue
            if not self._extract_years_from_text(item):
                filtered.append(item)
        return filtered

    @staticmethod
    def _params_contain_only_years_or_grand_prix(params: list[Any]) -> bool:
        if not params:
            return True
        for param in params:
            text = SponsorshipRecordSplitter._param_text(param)
            if SponsorshipRecordSplitter._is_year_param(param):
                continue
            if re.search(r"grand prix", text, flags=re.IGNORECASE):
                continue
            return False
        return True

    def _parse_grand_prix_scope(self, params: list[Any]) -> dict[str, Any] | None:
        if not params:
            return None
        if not self._params_contain_only_years_or_grand_prix(params):
            return None
        grand_prix_entries: list[dict[str, Any]] = []
        has_onwards = False
        range_scope: dict[str, Any] | None = None
        for param in params:
            if self._is_year_param(param):
                continue
            text = self._param_text(param)
            if not re.search(r"grand prix", text, flags=re.IGNORECASE):
                return None
            if re.search(r"\bonwards?\b", text, flags=re.IGNORECASE):
                has_onwards = True
            range_match = re.search(
                r"(.+?grand prix)\s+to\s+(.+?grand prix)",
                text,
                flags=re.IGNORECASE,
            )
            if range_match:
                start_text = self._clean_grand_prix_text(range_match.group(1))
                end_text = self._clean_grand_prix_text(range_match.group(2))
                range_scope = {
                    "type": "range",
                    "from": self._build_grand_prix_entry(param, start_text),
                    "to": self._build_grand_prix_entry(param, end_text),
                }
                continue
            cleaned = self._clean_grand_prix_text(text)
            if not cleaned:
                continue
            grand_prix_entries.append(self._build_grand_prix_entry(param, cleaned))

        if range_scope:
            return range_scope
        if has_onwards and grand_prix_entries:
            return {
                "type": "range",
                "from": grand_prix_entries[0],
                "to": None,
            }
        if grand_prix_entries:
            return {"type": "only", "grand_prix": grand_prix_entries}
        return None

    @staticmethod
    def _build_grand_prix_entry(param: Any, text: str) -> dict[str, Any]:
        if isinstance(param, dict) and param.get("url"):
            return {"text": text, "url": param["url"]}
        return {"text": text}

    def _filter_sponsors_for_year(self, sponsors: Any, year: int) -> Any:
        if not isinstance(sponsors, list):
            return sponsors
        filtered: list[Any] = []
        for item in sponsors:
            if isinstance(item, dict):
                params = item.get("params") or []
                if not self._params_contain_only_years_or_grand_prix(params):
                    cleaned_item = {k: v for k, v in item.items() if k != "params"}
                    filtered.append(cleaned_item)
                    continue
                year_params = self._extract_year_params(params)
                if not year_params or year in year_params:
                    cleaned_params = [
                        param for param in params if not self._is_year_param(param)
                    ]
                    if cleaned_params:
                        filtered.append({**item, "params": cleaned_params})
                    else:
                        cleaned_item = {k: v for k, v in item.items() if k != "params"}
                        filtered.append(cleaned_item)
                continue
            filtered.append(item)
        return filtered

    def _filter_colours_for_year(self, colours: Any, year: int) -> Any:
        if not isinstance(colours, list):
            return colours
        filtered: list[Any] = []
        for item in colours:
            if not isinstance(item, str):
                filtered.append(item)
                continue
            year_params = self._extract_years_from_text(item)
            if not year_params or year in year_params:
                if not year_params:
                    filtered.append(item)
                    continue
                if re.search(r"grand prix", item, flags=re.IGNORECASE):
                    filtered.append(self._strip_years_keep_context(item))
                else:
                    filtered.append(self._strip_year_suffix(item))
        return filtered

    def split_record_by_season(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        for key in self._colour_keys:
            if key in record:
                record = {**record, key: self._split_or_colours(record[key])}
        seasons = record.get("season")
        if not isinstance(seasons, list) or len(seasons) <= 1:
            return self._split_record_by_grand_prix(record)

        if not self._record_has_year_specific_sponsors(record):
            if self._record_has_year_specific_colours(record):
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
                    new_record[key] = self._filter_sponsors_for_year(record[key], year)
            for key in self._colour_keys:
                if key in record:
                    new_record[key] = self._filter_colours_for_year(record[key], year)
            split_records.extend(self._split_record_by_grand_prix(new_record))
        return split_records

    @staticmethod
    def _split_or_colours(colours: Any) -> Any:
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
                years = self._extract_years_from_text(item)
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
                    base_record[key] = self._remove_year_specific_colours(record[key])
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
                    scoped_record[key] = self._filter_colours_for_years(
                        record[key], years
                    )
            split_records.extend(self._split_record_by_grand_prix(scoped_record))

        return split_records

    @staticmethod
    def _parse_grand_prix_names(text: str) -> list[str]:
        text = re.sub(r"\bGrands Prix\b", "Grand Prix", text, flags=re.IGNORECASE)
        text = re.sub(r"\bGrand Prix\b", "", text, flags=re.IGNORECASE).strip()
        if text:
            parts = re.split(r"\s*(?:,| and )\s*", text)
            return [f"{part.strip()} Grand Prix" for part in parts if part.strip()]
        matches = re.findall(r"[^,;]+?Grand Prix", text, flags=re.IGNORECASE)
        return [clean_wiki_text(match) for match in matches if match.strip()] or [
            clean_wiki_text(text)
        ]

    def _colour_grand_prix_scope(
        self, colour: str
    ) -> tuple[dict[str, Any] | None, str]:
        match = re.search(r"\(([^)]*grand prix[^)]*)\)", colour, flags=re.IGNORECASE)
        cleaned_colour = self._strip_year_suffix(colour)
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
        names = self._parse_grand_prix_names(scope_text)
        scope = {
            "type": "only",
            "grand_prix": [{"text": name} for name in names],
        }
        return scope, cleaned_colour

    @staticmethod
    def _colour_is_replacement(record: Dict[str, Any], colour: str) -> bool:
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
                    scope = self._parse_grand_prix_scope(params)
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
                scope, cleaned = self._colour_grand_prix_scope(item)
                if scope:
                    scoped_list.append(
                        (scope, cleaned, self._colour_is_replacement(record, cleaned))
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
                scope_key = self._grand_prix_scope_key(scope)
                scope_entry = scope_map.setdefault(
                    scope_key, {"scope": scope, "items": {}}
                )
                scope_entry["items"].setdefault(key, []).append(item)

        for key, scoped_list in scoped_colours.items():
            for scope, colour, replace in scoped_list:
                scope_key = self._grand_prix_scope_key(scope)
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

    @staticmethod
    def _grand_prix_scope_key(scope: dict[str, Any]) -> tuple[Any, ...]:
        scope_type = scope.get("type")
        if scope_type == "only":
            entries = scope.get("grand_prix") or []
            key_entries = []
            for entry in entries:
                if isinstance(entry, dict):
                    key_entries.append((entry.get("text"), entry.get("url")))
                else:
                    key_entries.append((str(entry), None))
            return ("only", tuple(key_entries))
        if scope_type == "range":
            start = scope.get("from") or {}
            end = scope.get("to") or {}
            return (
                "range",
                start.get("text"),
                start.get("url"),
                end.get("text"),
                end.get("url"),
            )
        return ("other",)

    def _record_has_year_specific_sponsors(self, record: Dict[str, Any]) -> bool:
        for key in self._sponsor_keys:
            sponsors = record.get(key)
            if not isinstance(sponsors, list):
                continue
            for item in sponsors:
                if not isinstance(item, dict):
                    continue
                params = item.get("params") or []
                if not self._params_contain_only_years_or_grand_prix(params):
                    continue
                if self._extract_year_params(params):
                    return True
        return False

    def _record_has_year_specific_colours(self, record: Dict[str, Any]) -> bool:
        for key in self._colour_keys:
            colours = record.get(key)
            if not isinstance(colours, list):
                continue
            for item in colours:
                if isinstance(item, str) and self._extract_years_from_text(item):
                    return True
        return False
