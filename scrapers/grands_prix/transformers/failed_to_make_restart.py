from typing import List

from validation.records import ExportRecord
from scrapers.base.transformers import RecordTransformer


class FailedToMakeRestartTransformer(RecordTransformer):
    def transform(self, records: List[ExportRecord]) -> List[ExportRecord]:
        for row in records:
            drivers = row.pop("failed_to_make_restart_drivers", None)
            reason = row.pop("failed_to_make_restart_reason", None)
            if drivers is None and reason is None:
                continue
            row["failed_to_make_restart"] = {
                "drivers": drivers or [],
                "reason": reason,
            }
        return records


