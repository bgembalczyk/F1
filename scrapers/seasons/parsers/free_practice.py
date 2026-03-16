from typing import Any

from bs4 import BeautifulSoup

from models.services.rounds_service import parse_rounds
from scrapers.base.helpers.parsing import parse_int_from_text
from scrapers.base.table.columns.types.br_list import BrListColumn
from scrapers.base.table.columns.types.constructor import ConstructorColumn
from scrapers.base.table.columns.types.driver_list import DriverListColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.seasons.columns.driver_rounds import DriversWithRoundsColumn
from scrapers.seasons.parsers.table import SeasonTableParser


class SeasonFreePracticeParser:
    def __init__(self, table_parser: SeasonTableParser) -> None:
        self._table_parser = table_parser

    def parse(self, soup: BeautifulSoup) -> list[dict[str, Any]]:
        records = self._table_parser.parse_table(
            soup,
            section_ids=["Free_practice_drivers", "Friday_drivers"],
            expected_headers=["Constructor", "No.", "Driver name", "Rounds"],
            schema=TableSchemaDSL(
                columns=[
                    column("Constructor", "constructor", ConstructorColumn()),
                    column("No.", "numbers", BrListColumn()),
                    column("No", "numbers", BrListColumn()),
                    column("Driver name", "drivers", DriverListColumn()),
                    column("Driver", "drivers", DriverListColumn()),
                    column("Rounds", "rounds", BrListColumn()),
                ],
            ),
        )
        records = self._filter_source_footer_records(records)
        if records:
            return self._normalize_free_practice_records(records)

        records = self._table_parser.parse_table(
            soup,
            section_ids=["Free_practice_drivers"],
            expected_headers=["Constructor", "Driver name", "Rounds"],
            schema=TableSchemaDSL(
                columns=[
                    column("Constructor", "constructor", ConstructorColumn()),
                    column("Driver name", "drivers", DriverListColumn()),
                    column("Driver", "drivers", DriverListColumn()),
                    column("Rounds", "rounds", BrListColumn()),
                ],
            ),
        )
        records = self._filter_source_footer_records(records)
        if records:
            return self._normalize_free_practice_records(records)

        records = self._table_parser.parse_table(
            soup,
            section_ids=["Free_practice_drivers"],
            expected_headers=["Constructor", "Practice drivers"],
            schema=TableSchemaDSL(
                columns=[
                    column("Constructor", "constructor", ConstructorColumn()),
                    column(
                        "Practice drivers",
                        "practice_drivers",
                        DriversWithRoundsColumn(),
                    ),
                    column(
                        "Practice driver(s)",
                        "practice_drivers",
                        DriversWithRoundsColumn(),
                    ),
                ],
            ),
        )
        return self._filter_source_footer_records(records)

    def _filter_source_footer_records(
        self,
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return [
            record for record in records if not self._is_source_footer_record(record)
        ]

    def _is_source_footer_record(self, record: dict[str, Any]) -> bool:
        texts: list[str] = []
        texts.extend(self._constructor_texts(record.get("constructor")))
        texts.extend(self._driver_list_texts(record.get("drivers")))
        texts.extend(self._practice_driver_texts(record.get("practice_drivers")))
        if not texts:
            return False
        return all(text.lower().startswith("source") for text in texts)

    def _constructor_texts(self, value: Any) -> list[str]:
        texts: list[str] = []
        if isinstance(value, list):
            for item in value:
                texts.extend(self._constructor_texts(item))
            return texts
        if isinstance(value, dict):
            for key in ("chassis_constructor", "engine_constructor"):
                text = self._get_text(value.get(key))
                if text:
                    texts.append(text)
            return texts
        text = self._get_text(value)
        return [text] if text else []

    def _driver_list_texts(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        texts = []
        for item in value:
            text = self._get_text(item)
            if text:
                texts.append(text)
        return texts

    def _practice_driver_texts(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        texts = []
        for item in value:
            if not isinstance(item, dict):
                continue
            text = self._get_text(item.get("driver"))
            if text:
                texts.append(text)
        return texts

    @staticmethod
    def _get_text(value: Any) -> str | None:
        if isinstance(value, dict):
            text = value.get("text")
            if isinstance(text, str):
                return text
        if isinstance(value, str):
            return value
        return None

    @staticmethod
    def _normalize_free_practice_records(
        records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        normalized: list[dict[str, Any]] = []
        for record in records:
            drivers = record.pop("drivers", []) or []
            numbers = record.pop("numbers", []) or []
            rounds_list = record.pop("rounds", []) or []

            if len(numbers) == 1 and len(drivers) > 1:
                numbers = [numbers[0] for _ in range(len(drivers))]

            practice_drivers: list[dict[str, Any]] = []
            for index, driver in enumerate(drivers):
                if not driver:
                    continue
                entry: dict[str, Any] = {"driver": driver}

                if index < len(numbers):
                    number = parse_int_from_text(numbers[index])
                    if number is not None:
                        entry["no"] = number

                if index < len(rounds_list):
                    rounds_text = rounds_list[index]
                    rounds = parse_rounds(rounds_text)
                    if rounds_text or rounds:
                        entry["rounds"] = rounds

                practice_drivers.append(entry)

            record["practice_drivers"] = practice_drivers
            normalized.append(record)

        return normalized
