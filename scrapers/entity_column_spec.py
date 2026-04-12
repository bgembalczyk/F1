from dataclasses import dataclass

from scrapers.columns.base import BaseColumn


@dataclass(frozen=True)
class EntityColumnSpec:
    header: str
    output_key: str
    column_type: BaseColumn
