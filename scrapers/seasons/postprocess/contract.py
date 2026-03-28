from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from validation.validator_base import ExportRecord


class SeasonSectionContractPostProcessor:
    def post_process(self, records: list[ExportRecord]) -> list[ExportRecord]:
        for record in records:
            for key in ("regulation_changes", "mid_season_changes"):
                value = record.get(key)
                if value is None:
                    continue
                if not isinstance(value, list):
                    msg = f"Season postprocess contract violation: {key} must be list."
                    raise TypeError(msg)
        return records
