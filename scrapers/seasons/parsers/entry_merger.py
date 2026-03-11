from typing import Any
from typing import Dict
from typing import List

from models.services.rounds_service import RoundsService
from scrapers.base.helpers.parsing import parse_int_from_text


class EntryMerger:
    _DRIVER_FIELDS = {"race_drivers", "driver", "drivers", "rounds", "races", "no"}

    def merge_entries(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not records:
            return records

        keys = self._entry_group_keys(records)
        if not keys:
            merged: Dict[str, Any] = {}
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
            records: List[Dict[str, Any]],
            keys: List[str],
    ) -> Dict[str, Any]:
        if not keys:
            merged: Dict[str, Any] = {}
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
            records: List[Dict[str, Any]],
            key: str,
    ) -> Dict[str, Dict[str, Any]]:
        """Group records by the given key.

        Args:
            records: List of records to group
            key: Key to group by

        Returns:
            Dictionary mapping group_key to {"value": value, "records": [records]}
        """
        groups: Dict[str, Dict[str, Any]] = {}
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
            self, records: List[Dict[str, Any]],
    ) -> list[dict[str, Any]]:
        drivers: list[dict[str, Any]] = []
        for record in records:
            drivers.extend(self._extract_entry_drivers(record))
        return drivers

    @staticmethod
    def _strip_empty_entry_fields(record: Dict[str, Any]) -> None:
        for key in ("chassis", "engine", "tyre"):
            if record.get(key) is None:
                record.pop(key, None)

    @classmethod
    def _entry_group_keys(cls, records: List[Dict[str, Any]]) -> List[str]:
        keys: list[str] = []
        seen: set[str] = set()
        for record in records:
            for key in record.keys():
                if key in cls._DRIVER_FIELDS or key in seen:
                    continue
                seen.add(key)
                keys.append(key)
        return keys

    @staticmethod
    def _entry_group_key(value: Any) -> str:
        return repr(value)

    @staticmethod
    def _entry_merge_key(record: Dict[str, Any]) -> tuple[tuple[str, str], ...]:
        items: list[tuple[str, str]] = []
        for key, value in record.items():
            if key in {"race_drivers", "driver", "drivers", "rounds", "races", "no"}:
                continue
            items.append((key, repr(value)))
        return tuple(sorted(items))

    @staticmethod
    def _strip_entry_driver_fields(record: Dict[str, Any]) -> Dict[str, Any]:
        cleaned = dict(record)
        for key in ("race_drivers", "driver", "drivers", "rounds", "races", "no"):
            cleaned.pop(key, None)
        return cleaned

    def _extract_entry_drivers(self, record: Dict[str, Any]) -> list[dict[str, Any]]:
        drivers: list[dict[str, Any]] = []

        race_drivers = record.get("race_drivers")
        if isinstance(race_drivers, list):
            numbers = self._normalize_entry_numbers(record.get("no"))
            rounds_value = record.get("rounds") or record.get("races")
            rounds_by_index = (
                rounds_value
                if isinstance(rounds_value, list)
                   and len(rounds_value) == len(race_drivers)
                else None
            )
            rounds_all = (
                self._normalize_rounds(rounds_value) if rounds_by_index is None else []
            )
            numbers_by_index = numbers if len(numbers) == len(race_drivers) else []
            enriched: list[dict[str, Any]] = []
            for index, item in enumerate(race_drivers):
                entry = dict(item)
                if numbers_by_index:
                    entry.setdefault("no", numbers_by_index[index])
                elif numbers and len(numbers) == 1 and len(race_drivers) == 1:
                    entry.setdefault("no", numbers[0])
                if rounds_by_index is not None:
                    rounds = self._normalize_rounds(rounds_by_index[index])
                    if rounds:
                        entry["rounds"] = rounds
                elif rounds_all:
                    entry["rounds"] = rounds_all
                enriched.append(entry)
            drivers.extend(enriched)

        driver_value = record.get("driver")
        if driver_value is None:
            driver_value = record.get("drivers")

        if driver_value is None:
            return drivers

        driver_items = (
            driver_value if isinstance(driver_value, list) else [driver_value]
        )
        rounds_value = record.get("rounds") or record.get("races")
        numbers = self._normalize_entry_numbers(record.get("no"))
        numbers_by_index = numbers if len(numbers) == len(driver_items) else []

        if isinstance(rounds_value, list) and len(rounds_value) == len(driver_items):
            for driver, rounds_item in zip(driver_items, rounds_value):
                entry: dict[str, Any] = {"driver": driver}
                rounds = self._normalize_rounds(rounds_item)
                if rounds:
                    entry["rounds"] = rounds
                if numbers_by_index:
                    entry["no"] = numbers_by_index.pop(0)
                drivers.append(entry)
            return drivers

        rounds = self._normalize_rounds(rounds_value)
        for index, driver in enumerate(driver_items):
            entry = {"driver": driver}
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
            return RoundsService.parse_rounds(value)
        return []
