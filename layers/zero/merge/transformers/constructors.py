from __future__ import annotations

import re

from scrapers.wiki.constants import CHASSIS_CONSTRUCTOR_DOMAINS
from scrapers.wiki.constants import CONSTRUCTORS_FORMULA_ONE_FIELDS
from scrapers.wiki.constants import FORMER_CONSTRUCTORS_SOURCE
from scrapers.wiki.constants import INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE

from .base import DomainTransformStrategy
from .shared import build_racing_series
from .shared import ensure_constructor_status
from .shared import move_fields_to_formula_one


class ConstructorDomainTransformStrategy(DomainTransformStrategy):
    def __init__(self, domain: str) -> None:
        self._domain = domain

    def transform(self, record: dict[str, object], source_name: str) -> dict[str, object]:
        transformed = dict(record)
        if self._domain not in CHASSIS_CONSTRUCTOR_DOMAINS:
            return transformed

        if source_name == INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE:
            return self._transform_indianapolis_only_constructor(transformed)
        if source_name == FORMER_CONSTRUCTORS_SOURCE:
            return self._transform_former_constructor(transformed)

        constructor_fields = set(CONSTRUCTORS_FORMULA_ONE_FIELDS)
        if self._domain == "constructors" and re.fullmatch(r"f1_constructors_\d{4}\.json", source_name):
            constructor_fields.discard("engine")

        move_fields_to_formula_one(transformed, constructor_fields)
        ensure_constructor_status(transformed)
        return transformed

    def _transform_indianapolis_only_constructor(self, transformed: dict[str, object]) -> dict[str, object]:
        return {
            "constructor": {
                "text": transformed.get("constructor"),
                "url": transformed.get("constructor_url"),
            },
            "racing_series": {
                "AAA_national_championship": [],
                "formula_one": {
                    "status": "former",
                    "indianapolis_only": True,
                },
            },
        }

    def _transform_former_constructor(self, transformed: dict[str, object]) -> dict[str, object]:
        constructor = transformed.get("constructor")
        formula_one = {key: value for key, value in transformed.items() if key != "constructor"}
        formula_one["status"] = "former"
        return {
            "constructor": constructor,
            "racing_series": build_racing_series(formula_one),
        }
