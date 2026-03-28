from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.sections.contract_validation import validate_section_payloads

if TYPE_CHECKING:
    from validation.validator_base import ExportRecord


class CircuitSectionContractPostProcessor:
    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        for record in records:
            sections = record.get("sections")
            if isinstance(sections, list):
                validate_section_payloads(sections)
        return records
