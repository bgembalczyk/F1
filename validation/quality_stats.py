from dataclasses import dataclass
from dataclasses import field


@dataclass
class QualityStats:
    total_records: int = 0
    rejected_records: int = 0
    missing: dict[str, int] = field(default_factory=dict)
    types: dict[str, int] = field(default_factory=dict)
