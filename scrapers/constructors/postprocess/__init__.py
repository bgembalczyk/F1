from __future__ import annotations

from validation.validator_base import ExportRecord

from scrapers.base.sections.contract_validation import validate_section_payloads


class ConstructorSectionContractPostProcessor:
    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        for record in records:
            sections = record.get("sections")
            if isinstance(sections, list):
                validate_section_payloads(sections)
        return records
