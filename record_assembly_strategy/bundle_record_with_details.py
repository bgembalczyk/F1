from dataclasses import dataclass
from dataclasses import field
from typing import Any

from record_assembly_strategy.base import RecordAssemblyStrategy


@dataclass(frozen=True)
class BundleRecordWithDetailsStrategy(RecordAssemblyStrategy):
    record_field: str
    details_key: str = "details"
    details_default: dict[str, Any] = field(default_factory=dict)

    def assemble(
        self,
        record: dict[str, Any],
        details: dict[str, Any] | None,
    ) -> dict[str, Any]:
        record_value = record.get(self.record_field)
        return {
            self.record_field: record_value if isinstance(record_value, dict) else {},
            self.details_key: (
                details if details is not None else dict(self.details_default)
            ),
        }
