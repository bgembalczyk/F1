from __future__ import annotations

from typing import Any
from typing import Protocol


class MergeModel(Protocol):
    @classmethod
    def from_object(cls, value: object) -> MergeModel | None: ...
    def dedupe_key(self) -> str | None: ...
    def to_dict(self) -> dict[str, Any]: ...
