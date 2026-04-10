from dataclasses import dataclass
from typing import Any
from typing import TypeVar

ParserInputT = TypeVar("ParserInputT")


@dataclass(frozen=True)
class InfoboxExtractionResult:
    """Wspólny kontrakt wyniku ekstrakcji infoboxów."""

    records: list[dict[str, Any]]

    @property
    def primary_record(self) -> dict[str, Any]:
        return self.records[0] if self.records else {}
