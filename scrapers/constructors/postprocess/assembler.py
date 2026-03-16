from __future__ import annotations

from typing import Any


class ConstructorRecordAssembler:
    def assemble(
        self,
        *,
        url: str,
        infoboxes: list[dict[str, Any]],
        tables: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "url": url,
            "infoboxes": infoboxes,
            "tables": tables,
            "sections": sections,
        }
