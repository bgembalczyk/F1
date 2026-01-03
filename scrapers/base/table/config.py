from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, Sequence

from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.schema import TableSchema, TableSchemaBuilder


@dataclass(frozen=True)
class ScraperConfig:
    url: str
    section_id: Optional[str] = None
    expected_headers: Sequence[str] | None = None
    column_map: Mapping[str, str] = field(default_factory=dict)
    columns: Mapping[str, BaseColumn] = field(default_factory=dict)
    schema: TableSchema | TableSchemaBuilder | None = None
    table_css_class: str = "wikitable"
    record_factory: Callable[[dict[str, Any]], Any] | type | None = None
    model_class: type | None = None
    default_column: BaseColumn = field(default_factory=AutoColumn)

    def __post_init__(self) -> None:
        if self.schema is not None:
            schema = (
                self.schema.build()
                if isinstance(self.schema, TableSchemaBuilder)
                else self.schema
            )
            merged_column_map = {**schema.column_map, **self.column_map}
            merged_columns = {**schema.columns, **self.columns}
            object.__setattr__(self, "column_map", merged_column_map)
            object.__setattr__(self, "columns", merged_columns)
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.url, str) or not self.url.strip():
            raise ValueError("ScraperConfig.url must be a non-empty string.")

        if not isinstance(self.column_map, Mapping):
            raise TypeError("ScraperConfig.column_map must be a mapping.")

        for key, value in self.column_map.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError(
                    "ScraperConfig.column_map must map str keys to str values."
                )

        if not isinstance(self.columns, Mapping):
            raise TypeError("ScraperConfig.columns must be a mapping.")

        for key, value in self.columns.items():
            if not isinstance(key, str):
                raise ValueError("ScraperConfig.columns must use str keys.")
            if not isinstance(value, BaseColumn):
                raise ValueError(
                    "ScraperConfig.columns must map str keys to BaseColumn values."
                )

        if self.record_factory is not None and not callable(self.record_factory):
            raise TypeError("ScraperConfig.record_factory must be callable.")
