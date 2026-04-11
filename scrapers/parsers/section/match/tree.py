from dataclasses import dataclass
from typing import Any

SectionTree = dict[str, Any]


@dataclass(slots=True)
class SectionTreeMatch:
    section: SectionTree
    strategy: str
    score: float
