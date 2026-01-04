from typing import List

from scrapers.base.transformers.record_transformer import RecordTransformer
from validation.records import ExportRecord


class FatalitiesCarTransformer(RecordTransformer):
    def transform(self, records: List[ExportRecord]) -> List[ExportRecord]:
        for row in records:
            formula_category = row.pop("formula_category", None)
            if not formula_category:
                continue
            car = row.get("car")
            if isinstance(car, dict):
                car["formula_category"] = formula_category
            else:
                row["car"] = {
                    "text": car or "",
                    "url": None,
                    "formula_category": formula_category,
                }
        return records  # type: ignore[return-value]

