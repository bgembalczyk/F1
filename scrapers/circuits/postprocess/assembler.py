from __future__ import annotations

from typing import Any


class CircuitRecordAssembler:
    def assemble(
        self,
        *,
        url: str,
        infobox: dict[str, Any],
        tables: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "url": url,
            "infobox": infobox,
            "tables": tables,
            "sections": sections,
        }
