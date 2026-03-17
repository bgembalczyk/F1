from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from validation.validator_base import ExportRecord


class DriverSectionContractPostProcessor:
    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        for record in records:
            career_results = record.get("career_results")
            if not isinstance(career_results, list):
                continue
            for item in career_results:
                if not isinstance(item, dict):
                    msg = (
                        "Driver postprocess contract violation: "
                        "career_results item must be dict."
                    )
                    raise TypeError(msg)
                if not isinstance(item.get("section_id"), str):
                    msg = (
                        "Driver postprocess contract violation: "
                        "section_id must be str."
                    )
                    raise TypeError(msg)
                if not isinstance(item.get("section"), str):
                    msg = (
                        "Driver postprocess contract violation: "
                        "section label must be str."
                    )
                    raise TypeError(msg)
        return records
