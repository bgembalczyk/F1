from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from typing import Any
import warnings

from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.schema import TableSchema
from scrapers.base.table.schema import TableSchemaBuilder


@dataclass(frozen=True)
class TableScraperConfig:
    """Table extraction contract for a single source page/section.

    This config defines *what* should be extracted from HTML tables:
    source URL, optional section, expected headers, mapping/schema rules,
    column types and record factory/model binding.
    """

    url: str
    section_id: str | None = None
    expected_headers: Sequence[str] | None = None
    column_map: Mapping[str, str] = field(default_factory=dict)
    columns: Mapping[str, BaseColumn] = field(default_factory=dict)
    schema: TableSchema | TableSchemaBuilder | TableSchemaDSL | None = None
    table_css_class: str = "wikitable"
    record_factory: Callable[[dict[str, Any]], Any] | type | None = None
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
            msg = "TableScraperConfig.url must be a non-empty string."
            raise ValueError(msg)

        if not isinstance(self.column_map, Mapping):
            msg = "TableScraperConfig.column_map must be a mapping."
            raise TypeError(msg)

        for key, value in self.column_map.items():
            if not isinstance(key, str) or not isinstance(value, str):
                msg = "TableScraperConfig.column_map must map str keys to str values."
                raise TypeError(
                    msg,
                )

        if not isinstance(self.columns, Mapping):
            msg = "TableScraperConfig.columns must be a mapping."
            raise TypeError(msg)

        for key, value in self.columns.items():
            if not isinstance(key, str):
                msg = "TableScraperConfig.columns must use str keys."
                raise TypeError(msg)
            if not isinstance(value, BaseColumn):
                msg = "TableScraperConfig.columns must map str keys to BaseColumn values."
                raise TypeError(
                    msg,
                )

        if self.record_factory is not None and not callable(self.record_factory):
            msg = "TableScraperConfig.record_factory must be callable."
            raise TypeError(msg)


@dataclass(frozen=True)
class ScraperConfig(TableScraperConfig):
    """Deprecated alias for TableScraperConfig."""

    def __post_init__(self) -> None:
        warnings.warn(
            "ScraperConfig is deprecated; use TableScraperConfig instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__post_init__()
