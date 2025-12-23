from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence

from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn


@dataclass(frozen=True)
class ScraperConfig:
    url: str
    section_id: Optional[str] = None
    expected_headers: Sequence[str] | None = None
    column_map: Mapping[str, str] = field(default_factory=dict)
    columns: Mapping[str, BaseColumn] = field(default_factory=dict)
    table_css_class: str = "wikitable"
    model_class: type | None = None
    default_column: BaseColumn = field(default_factory=AutoColumn)

    def __post_init__(self) -> None:
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
