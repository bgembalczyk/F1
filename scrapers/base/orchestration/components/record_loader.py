from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RecordLoader:
    """Reads and normalizes records payload from JSON files."""

    def load(self, path: Path) -> list[dict[str, Any]]:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            records = payload.get("records", [])
            if isinstance(records, list):
                return [item for item in records if isinstance(item, dict)]
        return []
