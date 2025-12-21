from __future__ import annotations

from typing import Any, Dict


class InfoboxFieldMapper:
    """Mapuje surowe pola infoboxa do docelowego formatu."""

    def map(self, raw: Dict[str, Any] | None) -> Dict[str, Any]:
        if not raw:
            return {"title": None, "rows": {}}

        data = dict(raw)
        data.setdefault("title", None)
        data.setdefault("rows", {})
        return data
