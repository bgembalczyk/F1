from __future__ import annotations

import re

from .base import DomainTransformStrategy
from .shared import build_racing_series


class TeamsDomainTransformStrategy(DomainTransformStrategy):
    def transform(self, record: dict[str, object], source_name: str) -> dict[str, object]:
        transformed = dict(record)
        if re.fullmatch(r"f1_constructors_\d{4}\.json", source_name):
            transformed = {
                "team": transformed.get("constructor"),
                "racing_series": build_racing_series({**transformed}),
            }
        if source_name == "f1_sponsorship_liveries.json" and "liveries" in transformed:
            transformed["racing_series"] = build_racing_series({"liveries": transformed.pop("liveries")})
        if source_name == "f1_privateer_teams.json":
            formula_one = {key: transformed.pop(key) for key in ("seasons",) if key in transformed}
            formula_one["privateer"] = True
            transformed["racing_series"] = build_racing_series(formula_one)
        return transformed
