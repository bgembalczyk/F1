from __future__ import annotations

from scrapers.wiki.constants import CIRCUITS_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import FORMULA_ONE_SERIES

from .base import DomainTransformStrategy
from .shared import move_fields_to_formula_one


class CircuitsDomainTransformStrategy(DomainTransformStrategy):
    def transform(self, record: dict[str, object], source_name: str) -> dict[str, object]:
        _ = source_name
        transformed = dict(record)
        move_fields_to_formula_one(transformed, CIRCUITS_FORMULA_ONE_FIELDS)
        if "racing_series" not in transformed:
            transformed["series"] = FORMULA_ONE_SERIES.copy()
        return transformed
