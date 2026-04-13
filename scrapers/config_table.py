from __future__ import annotations

import warnings
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING

from scrapers.columns.base import BaseColumn
from scrapers.columns.spec import ColumnSpec
from scrapers.columns.types.auto import AutoColumn
from scrapers.schema_table import TableSchema
from scrapers.schema_table import TableSchemaBuilder
from scrapers.table_schema_dsl import TableSchemaDSL

if TYPE_CHECKING:
    from models.records.factories.protocol import RecordBuilder


@dataclass(frozen=True)
class TableConfig:
    url: str
    section_id: str | None = None
    expected_headers: Sequence[str] | None = None
    column_map: Mapping[str, str] = field(default_factory=dict)
    columns: Mapping[str, BaseColumn] = field(default_factory=dict)
    schema: TableSchema | TableSchemaBuilder | TableSchemaDSL | None = None
    table_css_class: str = "wikitable"
    record_factory: RecordBuilder | None = None
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
            msg = "TableConfig.url must be a non-empty string."
            raise ValueError(msg)

        if not isinstance(self.column_map, Mapping):
            msg = (
                "TableConfig.column_map must be of type Mapping; "
                f"got {type(self.column_map).__name__}."
            )
            raise TypeError(msg)

        for key, value in self.column_map.items():
            if not isinstance(key, str) or not isinstance(value, str):
                msg = (
                    "TableConfig.column_map must map str keys to str values; "
                    f"got key type {type(key).__name__} "
                    f"and value type {type(value).__name__}."
                )
                raise TypeError(msg)

        if not isinstance(self.columns, Mapping):
            msg = (
                "TableConfig.columns must be of type Mapping; "
                f"got {type(self.columns).__name__}."
            )
            raise TypeError(msg)

        for key, value in self.columns.items():
            if not isinstance(key, str):
                msg = (
                    "TableConfig.columns must use keys of type str; "
                    f"got {type(key).__name__}."
                )
                raise TypeError(msg)
            if not isinstance(value, BaseColumn):
                msg = (
                    "TableConfig.columns must map str keys to BaseColumn values; "
                    f"got value type {type(value).__name__}."
                )
                raise TypeError(msg)

        if (
            self.record_factory is not None
            and not hasattr(self.record_factory, "build")
            and not hasattr(self.record_factory, "create")
            and not callable(self.record_factory)
        ):
            msg = "TableConfig.record_factory must implement RecordBuilder.build() (or legacy create())."
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
) -> TableConfig:
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

    return TableConfig(
        url=url,
        section_id=section_id,
        expected_headers=expected_headers,
        record_factory=record_factory,
        model_class=model_class,
        table_css_class=table_css_class,
        schema=resolved_schema,
    )


def __getattr__(name: str) -> object:
    if name == "ScraperConfig":
        warnings.warn(
            "scrapers.config_table.ScraperConfig is deprecated; use TableConfig.",
            DeprecationWarning,
            stacklevel=2,
        )
        return TableConfig
    raise AttributeError(name)
