from __future__ import annotations

from scrapers.wiki.constants import GRANDS_PRIX_FORMULA_ONE_FIELDS

from .base import DomainTransformStrategy
from .shared import move_fields_to_formula_one


class GrandsPrixDomainTransformStrategy(DomainTransformStrategy):
    def transform(self, record: dict[str, object], source_name: str) -> dict[str, object]:
        _ = source_name
        transformed = dict(record)
        move_fields_to_formula_one(transformed, GRANDS_PRIX_FORMULA_ONE_FIELDS)
        return transformed
