from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING

from scrapers.base.table.columns.types import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.schema import TableSchema
from scrapers.base.table.schema import TableSchemaBuilder

if TYPE_CHECKING:
    from scrapers.base.factory.record_factory import RecordFactory
    from scrapers.base.table.dsl.column import ColumnSpec


@dataclass(frozen=True)
class ScraperConfig:
    url: str
    section_id: str | None = None
    expected_headers: Sequence[str] | None = None
    column_map: Mapping[str, str] = field(default_factory=dict)
    columns: Mapping[str, BaseColumn] = field(default_factory=dict)
    schema: TableSchema | TableSchemaBuilder | TableSchemaDSL | None = None
    table_css_class: str = "wikitable"
    record_factory: RecordFactory | None = None
    model_class: type | None = None
    default_column: BaseColumn = field(default_factory=AutoColumn)

    def __post_init__(self) -> None:
        if self.schema is not None:
            schema = self.schema
            if isinstance(self.schema, TableSchemaBuilder):
                schema = self.schema.build()
            if isinstance(self.schema, TableSchemaDSL):
                schema = self.schema.build()
            merged_column_map = {**schema.column_map, **self.column_map}
            merged_columns = {**schema.columns, **self.columns}
            object.__setattr__(self, "column_map", merged_column_map)
            object.__setattr__(self, "columns", merged_columns)
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.url, str) or not self.url.strip():
            msg = "ScraperConfig.url must be a non-empty string."
            raise ValueError(msg)

        if not isinstance(self.column_map, Mapping):
            msg = "ScraperConfig.column_map must be a mapping."
            raise TypeError(msg)

        for key, value in self.column_map.items():
            if not isinstance(key, str) or not isinstance(value, str):
                msg = "ScraperConfig.column_map must map str keys to str values."
                raise TypeError(
                    msg,
                )

        if not isinstance(self.columns, Mapping):
            msg = "ScraperConfig.columns must be a mapping."
            raise TypeError(msg)

        for key, value in self.columns.items():
            if not isinstance(key, str):
                msg = "ScraperConfig.columns must use str keys."
                raise TypeError(msg)
            if not isinstance(value, BaseColumn):
                msg = "ScraperConfig.columns must map str keys to BaseColumn values."
                raise TypeError(
                    msg,
                )

        if self.record_factory is not None and not hasattr(
            self.record_factory,
            "create",
        ):
            msg = "ScraperConfig.record_factory must implement RecordFactory.create()."
            raise TypeError(msg)


def build_scraper_config(
    *,
    url: str,
    columns: Sequence[ColumnSpec] | None = None,
    schema: TableSchema | TableSchemaBuilder | TableSchemaDSL | None = None,
    section_id: str | None = None,
    expected_headers: Sequence[str] | None = None,
    table_css_class: str = "wikitable",
    record_factory=None,
    model_class: type | None = None,
) -> ScraperConfig:
    """Canonical builder for table-based scraper configuration."""
    if columns is None and schema is None:
        msg = "Either columns or schema must be provided."
        raise ValueError(msg)

    if columns is not None and schema is not None:
        msg = "Provide only one of columns or schema."
        raise ValueError(msg)

    resolved_schema = (
        TableSchemaDSL(columns=list(columns or [])).build()
        if columns is not None
        else schema
    )

    return ScraperConfig(
        url=url,
        section_id=section_id,
        expected_headers=expected_headers,
        record_factory=record_factory,
        model_class=model_class,
        table_css_class=table_css_class,
        schema=resolved_schema,
    )
