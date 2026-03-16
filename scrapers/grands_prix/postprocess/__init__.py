from __future__ import annotations

from validation.validator_base import ExportRecord


class GrandPrixSectionContractPostProcessor:
    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        for record in records:
            section_id = record.get("section_id")
            by_year = record.get("by_year")
            if section_id is not None and not isinstance(section_id, str):
                raise ValueError(
                    "Grand prix postprocess contract violation: section_id must be str.",
                )
            if by_year is not None and not isinstance(by_year, list):
                raise ValueError(
                    "Grand prix postprocess contract violation: by_year must be list.",
                )
        return records
