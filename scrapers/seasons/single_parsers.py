from __future__ import annotations

from typing import Any, Dict, List

from bs4 import BeautifulSoup

from scrapers.base.helpers.parsing import parse_int_from_text
from scrapers.base.options import ScraperOptions
from scrapers.base.table.columns.types.int import IntColumn
from scrapers.base.table.columns.types.points import PointsColumn
from scrapers.base.table.columns.types.position import PositionColumn
from scrapers.base.table.columns.types.race_result import RaceResultColumn
from scrapers.base.table.config import ScraperConfig
from scrapers.base.table.parser import HtmlTableParser
from scrapers.base.table.pipeline import TablePipeline
from scrapers.seasons.standings_scraper import F1StandingsScraper
from models.services.rounds_service import RoundsService


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
        groups: dict[str, dict[str, Any]] = {}

        for record in records:
            value = record.get(root_key)
            group_key = self._entry_group_key(value)
            group = groups.get(group_key)
            if group is None:
                group = {"value": value, "records": []}
                groups[group_key] = group
            group["records"].append(record)

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
        groups: dict[str, dict[str, Any]] = {}

        for record in records:
            value = record.get(key)
            group_key = self._entry_group_key(value)
            group = groups.get(group_key)
            if group is None:
                group = {"value": value, "records": []}
                groups[group_key] = group
            group["records"].append(record)

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

    def _merge_entry_drivers(
        self, records: List[Dict[str, Any]]
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


class SeasonTableParser:
    def __init__(
        self,
        *,
        options: ScraperOptions,
        include_urls: bool,
        url: str,
    ) -> None:
        self._options = options
        self._include_urls = include_urls
        self._skip_sentinel = object()
        self.url = url

    def update_url(self, url: str) -> None:
        self.url = url

    def parse_standings_table(
        self,
        soup: BeautifulSoup,
        *,
        section_ids: list[str],
        subject_header: str,
        subject_key: str,
        subject_column: Any,
    ) -> List[Dict[str, Any]]:
        for section_id in section_ids:
            config = ScraperConfig(
                url=self.url,
                section_id=section_id,
                expected_headers=[subject_header],
                column_map={
                    "Pos.": "pos",
                    "Pos": "pos",
                    subject_header: subject_key,
                    "Points": "points",
                    "Pts.": "points",
                    "Pts": "points",
                    "No.": "no",
                    "No": "no",
                },
                columns={
                    "pos": PositionColumn(),
                    subject_key: subject_column,
                    "points": PointsColumn(),
                    "no": IntColumn(),
                },
                default_column=RaceResultColumn(),
            )
            scraper = F1StandingsScraper(options=self._options, config=config)
            try:
                records = scraper.parse(soup)
                if records:
                    return records
            except RuntimeError:
                continue
        return []

    def parse_table(
        self,
        soup: BeautifulSoup,
        *,
        section_ids: list[str],
        expected_headers: list[str],
        column_map: dict[str, str],
        columns: dict[str, Any],
        default_column: Any | None = None,
    ) -> List[Dict[str, Any]]:
        for section_id in section_ids:
            config = ScraperConfig(
                url=self.url,
                section_id=section_id,
                expected_headers=expected_headers,
                column_map=column_map,
                columns=columns,
                default_column=default_column,
            )
            pipeline = TablePipeline(
                config=config,
                include_urls=self._include_urls,
                skip_sentinel=self._skip_sentinel,
            )
            parser = HtmlTableParser(
                section_id=pipeline.section_id,
                fragment=pipeline.fragment,
                expected_headers=pipeline.expected_headers,
                table_css_class=pipeline.table_css_class,
            )
            try:
                records: List[Dict[str, Any]] = []
                for row_index, row in enumerate(parser.parse(soup)):
                    record = pipeline.parse_cells(
                        row.headers,
                        row.cells,
                        row_index=row_index,
                    )
                    if record:
                        records.append(record)
                if records:
                    return records
            except RuntimeError:
                continue

        return []
