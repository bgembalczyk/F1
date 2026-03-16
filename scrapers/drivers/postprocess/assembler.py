from __future__ import annotations

from typing import Any


class DriverRecordAssembler:
    def assemble(
        self,
        *,
        url: str,
        infobox: dict[str, Any],
        career_results: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "url": url,
            "infobox": infobox,
            "career_results": career_results,
        }
