from __future__ import annotations

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
