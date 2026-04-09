from dataclasses import dataclass
from typing import Any

from record_assembly_strategy.base import RecordAssemblyStrategy


@dataclass(frozen=True)
class AttachDetailsStrategy(RecordAssemblyStrategy):
    details_key: str = "details"

    def assemble(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        assembled = dict(record)
        assembled[self.details_key] = details
        return assembled
