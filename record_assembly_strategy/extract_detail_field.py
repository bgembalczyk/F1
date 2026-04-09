from dataclasses import dataclass
from typing import Any

from record_assembly_strategy.base import RecordAssemblyStrategy


@dataclass(frozen=True)
class ExtractDetailFieldStrategy(RecordAssemblyStrategy):
    detail_field: str
    target_key: str | None = None

    def assemble(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        assembled = dict(record)
        target_key = self.target_key or self.detail_field
        assembled[target_key] = (
            details.get(self.detail_field) if isinstance(details, dict) else None
        )
        return assembled
