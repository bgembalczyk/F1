from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scrapers.base.sections.constants import SECTION_RESULT_KEYS
from scrapers.base.sections.contract_validation import validate_section_result_payload


@dataclass(frozen=True)
class SectionRecordInput:
    """Input contract for section -> record mapper.

    Required keys:
    - section_id: str
    - section_label: str
    - records: list[dict[str, Any]]
    - metadata: dict[str, Any]
    """

    payload: dict[str, Any]


class SectionRecordMapper:
    """Maps a section payload to a normalized export record.

    Normalization rules:
    - validates section payload contract and key order,
    - trims section_id/section_label,
    - returns shallow copies of records and metadata containers.
    """

    def map(self, payload: SectionRecordInput | dict[str, Any]) -> dict[str, Any]:
        source = payload.payload if isinstance(payload, SectionRecordInput) else payload
        validate_section_result_payload(source)
        section_id = source["section_id"].strip()
        section_label = source["section_label"].strip()
        return {
            "section_id": section_id,
            "section_label": section_label,
            "records": list(source["records"]),
            "metadata": dict(source["metadata"]),
        }

    def map_many(self, payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [self.map(payload) for payload in payloads]


__all__ = [
    "SECTION_RESULT_KEYS",
    "SectionRecordInput",
    "SectionRecordMapper",
]
