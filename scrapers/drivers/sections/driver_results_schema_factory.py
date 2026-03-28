from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from models.value_objects.enums import TableType
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.drivers.columns.round import RoundColumn
from scrapers.drivers.columns.unknown_value import UnknownValueColumn
from scrapers.drivers.sections.constants import CAREER_HIGHLIGHTS_COLUMN_FACTORY_BY_KEY
from scrapers.drivers.sections.constants import CAREER_HIGHLIGHTS_HEADER_TO_KEY
from scrapers.drivers.sections.constants import CAREER_SUMMARY_COLUMN_FACTORY_BY_KEY
from scrapers.drivers.sections.constants import CAREER_SUMMARY_HEADER_TO_KEY
from scrapers.drivers.sections.constants import COMPLETE_RESULTS_COLUMN_FACTORY_BY_KEY
from scrapers.drivers.sections.constants import COMPLETE_RESULTS_HEADER_TO_KEY

if TYPE_CHECKING:
    from scrapers.base.table.columns.types.base import BaseColumn


class DriverResultsSchemaFactory:
    def __init__(self, *, unknown_value: str) -> None:
        self._unknown_value = unknown_value

    def build(self, *, table_type: TableType | str, headers: list[str]) -> TableSchemaDSL:
        parsed_table_type = TableType.from_raw(table_type)
        if parsed_table_type is TableType.CAREER_HIGHLIGHTS:
            return self._build_from_maps(
                header_to_key=CAREER_HIGHLIGHTS_HEADER_TO_KEY,
                column_factory_by_key=CAREER_HIGHLIGHTS_COLUMN_FACTORY_BY_KEY,
            )
        if parsed_table_type is TableType.CAREER_SUMMARY:
            return self._build_from_maps(
                header_to_key=CAREER_SUMMARY_HEADER_TO_KEY,
                column_factory_by_key=CAREER_SUMMARY_COLUMN_FACTORY_BY_KEY,
            )
        if parsed_table_type is TableType.COMPLETE_RESULTS:
            schema_columns = self._build_from_maps(
                header_to_key=COMPLETE_RESULTS_HEADER_TO_KEY,
                column_factory_by_key=COMPLETE_RESULTS_COLUMN_FACTORY_BY_KEY,
            ).columns
            schema_columns.extend(
                column(header, header, self._unknown(RoundColumn()))
                for header in headers
                if header.isdigit()
            )
            return TableSchemaDSL(columns=schema_columns)
        msg = f"Unsupported table_type: {parsed_table_type.to_export()}"
        raise ValueError(msg)

    def _build_from_maps(
        self,
        *,
        header_to_key: dict[str, str],
        column_factory_by_key: dict[str, Any],
    ) -> TableSchemaDSL:
        return TableSchemaDSL(
            columns=[
                column(
                    header,
                    key,
                    self._unknown(column_factory_by_key[key]()),
                )
                for header, key in header_to_key.items()
            ],
        )

    def _unknown(self, base_column: BaseColumn) -> UnknownValueColumn:
        return UnknownValueColumn(base_column, unknown_value=self._unknown_value)
