from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ResolvedInput:
    records: list[dict[str, Any]]
    source_path: Path
