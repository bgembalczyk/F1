from __future__ import annotations

from .base import DomainTransformStrategy
from .shared import extract_red_flag
from .shared import pop_red_flag_fields


class RacesDomainTransformStrategy(DomainTransformStrategy):
    def transform(self, record: dict[str, object], source_name: str) -> dict[str, object]:
        transformed = dict(record)
        if source_name == "f1_red_flagged_world_championship_races.json":
            transformed["championship"] = True
        if source_name == "f1_red_flagged_non_championship_races.json":
            transformed["championship"] = False
        transformed["red_flag"] = extract_red_flag(transformed)
        pop_red_flag_fields(transformed)
        return transformed
