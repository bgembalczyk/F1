from __future__ import annotations

from scrapers.wiki.constants import ENGINES_FORMULA_ONE_FIELDS

from .base import DomainTransformStrategy
from .shared import move_fields_to_formula_one


class EnginesDomainTransformStrategy(DomainTransformStrategy):
    def transform(self, record: dict[str, object], source_name: str) -> dict[str, object]:
        transformed = dict(record)
        if source_name == "f1_indianapolis_only_engine_manufacturers.json":
            transformed["racing_series"] = {
                "AAA_national_championship": [],
                "formula_one": {"status": "former", "indianapolis_only": True},
            }
        elif source_name == "f1_engine_manufacturers.json":
            move_fields_to_formula_one(transformed, ENGINES_FORMULA_ONE_FIELDS)
        return transformed
