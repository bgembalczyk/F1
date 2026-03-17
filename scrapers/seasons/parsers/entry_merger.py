from typing import Any

from models.services.rounds_service import parse_rounds
from scrapers.base.helpers.parsing import parse_int_from_text
from scrapers.seasons.parsers.constants import DRIVER_FIELDS


class EntryMerger:
    def merge_entries(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not records:
            return records

        keys = self._entry_group_keys(records)
        if not keys:
            merged: dict[str, Any] = {}
            drivers = self._merge_entry_drivers(records)
            if drivers:
                merged["race_drivers"] = drivers
            return [merged]

        root_key = keys[0]
        groups = self._group_records_by_key(records, root_key)

        merged_records: list[dict[str, Any]] = []
        for group in groups.values():
            item = {root_key: group["value"]}
            item.update(self._merge_entry_groups(group["records"], keys[1:]))
            self._strip_empty_entry_fields(item)
            merged_records.append(item)

        return merged_records

    def _merge_entry_groups(
        self,
        records: list[dict[str, Any]],
        keys: list[str],
    ) -> dict[str, Any]:
        if not keys:
            merged: dict[str, Any] = {}
            drivers = self._merge_entry_drivers(records)
            if drivers:
                merged["race_drivers"] = drivers
            return merged

        key = keys[0]
        groups = self._group_records_by_key(records, key)

        if len(groups) == 1:
            group = next(iter(groups.values()))
            merged = {key: group["value"]}
            merged.update(self._merge_entry_groups(group["records"], keys[1:]))
            return merged

        items: list[dict[str, Any]] = []
        for group in groups.values():
            item: dict[str, Any] = {}
            if key == "constructor" and isinstance(group["value"], dict):
                item.update(group["value"])
            else:
                item[key] = group["value"]
            item.update(self._merge_entry_groups(group["records"], keys[1:]))
            items.append(item)

        return {key: items}

    def _group_records_by_key(
        self,
        records: list[dict[str, Any]],
        key: str,
    ) -> dict[str, dict[str, Any]]:
        groups: dict[str, dict[str, Any]] = {}
        for record in records:
            value = record.get(key)
            group_key = self._entry_group_key(value)
            group = groups.get(group_key)
            if group is None:
                group = {"value": value, "records": []}
                groups[group_key] = group
            group["records"].append(record)
        return groups

    def _merge_entry_drivers(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        drivers: list[dict[str, Any]] = []
        for record in records:
            drivers.extend(self._extract_entry_drivers(record))
        return drivers

    @staticmethod
    def _strip_empty_entry_fields(record: dict[str, Any]) -> None:
        for key in ("chassis", "engine", "tyre"):
            if record.get(key) is None:
                record.pop(key, None)

    @classmethod
    def _entry_group_keys(cls, records: list[dict[str, Any]]) -> list[str]:
        keys: list[str] = []
        seen: set[str] = set()
        for record in records:
            for key in record:
                if key in DRIVER_FIELDS or key in seen:
                    continue
                seen.add(key)
                keys.append(key)
        return keys

    @staticmethod
    def _entry_group_key(value: Any) -> str:
        return repr(value)

    @staticmethod
    def _entry_merge_key(record: dict[str, Any]) -> tuple[tuple[str, str], ...]:
        items: list[tuple[str, str]] = []
        for key, value in record.items():
            if key in {"race_drivers", "driver", "drivers", "rounds", "races", "no"}:
                continue
            items.append((key, repr(value)))
        return tuple(sorted(items))

    @staticmethod
    def _strip_entry_driver_fields(record: dict[str, Any]) -> dict[str, Any]:
        cleaned = dict(record)
        for key in ("race_drivers", "driver", "drivers", "rounds", "races", "no"):
            cleaned.pop(key, None)
        return cleaned

    def _extract_entry_drivers(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        race_driver_records = self._extract_race_driver_records(record)
        fallback_driver_records = self._extract_fallback_driver_records(record)
        return race_driver_records + fallback_driver_records

    def _extract_race_driver_records(
        self,
        record: dict[str, Any],
    ) -> list[dict[str, Any]]:
        race_drivers = record.get("race_drivers")
        if not isinstance(race_drivers, list):
            return []

        numbers = self._normalize_entry_numbers(record.get("no"))
        rounds_value = record.get("rounds") or record.get("races")
        rounds_by_index = self._rounds_by_index(rounds_value, len(race_drivers))
        rounds_all = (
            [] if rounds_by_index is not None else self._normalize_rounds(rounds_value)
        )
        numbers_by_index = numbers if len(numbers) == len(race_drivers) else []

        enriched: list[dict[str, Any]] = []
        for index, item in enumerate(race_drivers):
            entry = dict(item)
            self._add_number(entry, numbers, numbers_by_index, index, len(race_drivers))
            self._add_rounds(entry, rounds_by_index, rounds_all, index)
            enriched.append(entry)
        return enriched

    def _extract_fallback_driver_records(
        self,
        record: dict[str, Any],
    ) -> list[dict[str, Any]]:
        driver_value = record.get("driver")
        if driver_value is None:
            driver_value = record.get("drivers")
        if driver_value is None:
            return []

        driver_items = (
            driver_value if isinstance(driver_value, list) else [driver_value]
        )
        rounds_value = record.get("rounds") or record.get("races")
        numbers = self._normalize_entry_numbers(record.get("no"))
        numbers_by_index = numbers if len(numbers) == len(driver_items) else []

        if isinstance(rounds_value, list) and len(rounds_value) == len(driver_items):
            return self._build_drivers_with_indexed_rounds(
                driver_items,
                rounds_value,
                numbers_by_index,
            )

        rounds = self._normalize_rounds(rounds_value)
        return self._build_drivers_with_shared_rounds(
            driver_items,
            rounds,
            numbers,
            numbers_by_index,
        )

    @staticmethod
    def _rounds_by_index(rounds_value: Any, size: int) -> list[Any] | None:
        if isinstance(rounds_value, list) and len(rounds_value) == size:
            return rounds_value
        return None

    def _add_number(
        self,
        entry: dict[str, Any],
        numbers: list[int],
        numbers_by_index: list[int],
        index: int,
        total_drivers: int,
    ) -> None:
        if numbers_by_index:
            entry.setdefault("no", numbers_by_index[index])
            return
        if numbers and len(numbers) == 1 and total_drivers == 1:
            entry.setdefault("no", numbers[0])

    def _add_rounds(
        self,
        entry: dict[str, Any],
        rounds_by_index: list[Any] | None,
        rounds_all: list[int],
        index: int,
    ) -> None:
        if rounds_by_index is not None:
            rounds = self._normalize_rounds(rounds_by_index[index])
            if rounds:
                entry["rounds"] = rounds
            return
        if rounds_all:
            entry["rounds"] = rounds_all

    def _build_drivers_with_indexed_rounds(
        self,
        driver_items: list[Any],
        rounds_values: list[Any],
        numbers_by_index: list[int],
    ) -> list[dict[str, Any]]:
        drivers: list[dict[str, Any]] = []
        for index, (driver, rounds_item) in enumerate(
            zip(driver_items, rounds_values, strict=False),
        ):
            entry: dict[str, Any] = {"driver": driver}
            rounds = self._normalize_rounds(rounds_item)
            if rounds:
                entry["rounds"] = rounds
            if numbers_by_index:
                entry["no"] = numbers_by_index[index]
            drivers.append(entry)
        return drivers

    def _build_drivers_with_shared_rounds(
        self,
        driver_items: list[Any],
        rounds: list[int],
        numbers: list[int],
        numbers_by_index: list[int],
    ) -> list[dict[str, Any]]:
        drivers: list[dict[str, Any]] = []
        for index, driver in enumerate(driver_items):
            entry: dict[str, Any] = {"driver": driver}
            if rounds:
                entry["rounds"] = rounds
            if numbers_by_index:
                entry["no"] = numbers_by_index[index]
            elif numbers and len(numbers) == 1 and len(driver_items) == 1:
                entry["no"] = numbers[0]
            drivers.append(entry)
        return drivers

    @staticmethod
    def _normalize_entry_numbers(value: Any) -> list[int]:
        if value is None:
            return []
        if isinstance(value, list):
            numbers: list[int] = []
            for item in value:
                if isinstance(item, int):
                    numbers.append(item)
                elif isinstance(item, str):
                    parsed = parse_int_from_text(item)
                    if parsed is not None:
                        numbers.append(parsed)
            return numbers
        if isinstance(value, int):
            return [value]
        if isinstance(value, str):
            parsed = parse_int_from_text(value)
            return [parsed] if parsed is not None else []
        return []

    @staticmethod
    def _normalize_rounds(value: Any) -> list[int]:
        if value is None:
            return []
        if isinstance(value, list) and all(isinstance(v, int) for v in value):
            return list(value)
        if isinstance(value, int):
            return [value]
        if isinstance(value, str):
            return parse_rounds(value)
        return []
