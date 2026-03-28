from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.normalization import EmptyValuePolicy
from scrapers.base.normalization_pipeline import normalize_value
from scrapers.base.transformers.record_transformer import RecordTransformer

if TYPE_CHECKING:
    from collections.abc import Iterable

    from validation.validator_base import ExportRecord


class NormalizeLinksTransformer(RecordTransformer):
    def __init__(
        self,
        *,
        drop_empty: bool = True,
        strip_marks: bool = True,
        strip_lang_suffix: bool = True,
        empty_value_policy: EmptyValuePolicy = EmptyValuePolicy.NORMALIZE,
    ) -> None:
        super().__init__(empty_value_policy=empty_value_policy)
        self.drop_empty = drop_empty
        self.strip_marks = strip_marks
        self.strip_lang_suffix = strip_lang_suffix

    def transform(self, records: list[ExportRecord]) -> list[ExportRecord]:
        normalized_records: list[ExportRecord] = []
        for record in records:
            if not isinstance(record, dict):
                normalized_records.append(record)
                continue
            updated: ExportRecord = dict(record)
            for key, value in record.items():
                updated[key] = normalize_value(
                    value,
                    strip_marks=self.strip_marks,
                    drop_empty=self.drop_empty,
                    strip_lang_suffix=self.strip_lang_suffix,
                    empty_value_policy=self.empty_value_policy,
                    drop_empty_text=False,
                )
            normalized_records.append(updated)
        return normalized_records
