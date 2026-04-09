from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ExecutedStep:
    records: list[dict[str, Any]]
    errors: list[str]
    duration_ms: float
