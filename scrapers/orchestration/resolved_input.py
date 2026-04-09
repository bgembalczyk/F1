from dataclasses import dataclass
from typing import Any

from pathlib import Path


@dataclass(frozen=True)
class ResolvedInput:
    records: list[dict[str, Any]]
    source_path: Path
