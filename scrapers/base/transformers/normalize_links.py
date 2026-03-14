from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.links import normalize_single_link
from scrapers.base.normalization import EmptyValuePolicy
from scrapers.base.transformers.record_transformer import RecordTransformer
from validation.records import ExportRecord

LINK_KEYS = {"text", "url"}


def is_link_record(value: dict[str, Any]) -> bool:
    if not value:
        return False
    keys = set(value.keys())
    if not keys.issubset(LINK_KEYS):
        return False
    return bool(keys & LINK_KEYS)


def is_link_list(value: Iterable[Any]) -> bool:
    return all(isinstance(item, dict) and is_link_record(item) for item in value)


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
                if isinstance(value, dict) and is_link_record(value):
                    updated[key] = normalize_single_link(
                        value,
                        strip_marks_text=self.strip_marks,
                        drop_empty=self.drop_empty,
                        strip_lang_suffix=self.strip_lang_suffix,
                    )
                    continue
                if isinstance(value, list) and is_link_list(value):
                    updated[key] = normalize_links(
                        value,
                        strip_marks=self.strip_marks,
                        drop_empty=self.drop_empty,
                        strip_lang_suffix=self.strip_lang_suffix,
                    )
            normalized_records.append(updated)
        return normalized_records
