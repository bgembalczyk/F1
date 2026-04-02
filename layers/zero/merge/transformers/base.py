from __future__ import annotations

from typing import Protocol


class DomainTransformStrategy(Protocol):
    def transform(self, record: dict[str, object], source_name: str) -> dict[str, object]:
        ...
