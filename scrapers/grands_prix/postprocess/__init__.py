from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from validation.validator_base import ExportRecord


class GrandPrixSectionContractPostProcessor:
    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        for record in records:
            section_id = record.get("section_id")
            by_year = record.get("by_year")
            if section_id is not None and not isinstance(section_id, str):
                msg = (
                    "Grand prix postprocess contract violation: "
                    "section_id must be str."
                )
                raise ValueError(msg)
            if by_year is not None and not isinstance(by_year, list):
                msg = (
                    "Grand prix postprocess contract violation: "
                    "by_year must be list."
                )
                raise ValueError(msg)
        return records
