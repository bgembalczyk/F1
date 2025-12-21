from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

try:
    import pandas as pd

    _HAS_PANDAS = True
except Exception:  # opcjonalne
    _HAS_PANDAS = False


class DataExporter:
    def to_json(
        self,
        result: ScrapeResult | List[Dict[str, Any]],
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        payload = self._json_payload(result, include_metadata=include_metadata)
        path = Path(path)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=indent), encoding="utf-8"
        )

    def to_csv(
        self,
        result: ScrapeResult | List[Dict[str, Any]],
        path: str | Path,
        *,
        fieldnames: Optional[Sequence[str]] = None,
    ) -> None:
        data = self._extract_data(result)
        if not data:
            return

        path = Path(path)

        # Jeżeli nie podano fieldnames – bierzemy wszystkie klucze z unią
        if fieldnames is None:
            keys: List[str] = []
            for row in data:
                for key in row.keys():
                    if key not in keys:
                        keys.append(key)
            fieldnames = keys

        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

    def to_dataframe(self, result: ScrapeResult | List[Dict[str, Any]]):
        if not _HAS_PANDAS:
            raise RuntimeError("Pandas nie jest zainstalowane.")
        return pd.DataFrame(self._extract_data(result))

    def _extract_data(
        self, result: ScrapeResult | List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        if isinstance(result, ScrapeResult):
            return result.data
        return result

    def _json_payload(
        self,
        result: ScrapeResult | List[Dict[str, Any]],
        *,
        include_metadata: bool,
    ) -> Any:
        if not include_metadata:
            return self._extract_data(result)

        if isinstance(result, ScrapeResult):
            return {
                "meta": {
                    "source_url": result.source_url,
                    "timestamp": result.timestamp.isoformat(),
                },
                "data": result.data,
            }

        return {"meta": None, "data": result}


@dataclass(frozen=True)
class ScrapeResult:
    data: List[Dict[str, Any]]
    source_url: Optional[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    exporter: Optional[DataExporter] = None

    def __post_init__(self) -> None:
        if self.exporter is None:
            object.__setattr__(self, "exporter", DataExporter())

    def to_json(
        self,
        path: str | Path,
        *,
        indent: int = 2,
        include_metadata: bool = False,
    ) -> None:
        self.exporter.to_json(
            self, path, indent=indent, include_metadata=include_metadata
        )

    def to_csv(
        self,
        path: str | Path,
        *,
        fieldnames: Optional[Sequence[str]] = None,
    ) -> None:
        self.exporter.to_csv(self, path, fieldnames=fieldnames)

    def to_dataframe(self):
        return self.exporter.to_dataframe(self)
