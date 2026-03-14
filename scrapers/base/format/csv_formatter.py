import csv
import io
import json
from collections.abc import Sequence

from scrapers.base.export.metadata import ExportMetadata
from scrapers.base.format.formatter_helpers import extract_data
from scrapers.base.results import ScrapeResult


class CsvFormatter:
    @staticmethod
    def format(
        result: ScrapeResult,
        *,
        fieldnames: Sequence[str] | None = None,
        include_metadata: bool = False,
    ) -> str:
        data = extract_data(result)
        output = io.StringIO()
        if include_metadata:
            metadata = ExportMetadata.from_result(result)
            output.write(
                f"# meta: {json.dumps(metadata.to_dict(), ensure_ascii=False)}\n",
            )
        if not data:
            return output.getvalue()

        if fieldnames is None:
            keys: list[str] = []
            for row in data:
                for key in row.keys():
                    if key not in keys:
                        keys.append(key)
            fieldnames = keys

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
        return output.getvalue()
