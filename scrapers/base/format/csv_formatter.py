from __future__ import annotations

import csv
import io
from typing import List, Optional, Sequence

from scrapers.base.format.formatter_helpers import _extract_data
from scrapers.base.results import ScrapeResult


class CsvFormatter:
    def format(
        self,
        result: ScrapeResult,
        *,
        fieldnames: Optional[Sequence[str]] = None,
    ) -> str:
        data = _extract_data(result)
        if not data:
            return ""

        if fieldnames is None:
            keys: List[str] = []
            for row in data:
                for key in row.keys():
                    if key not in keys:
                        keys.append(key)
            fieldnames = keys

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return output.getvalue()
