from typing import Any
from typing import List

from models.records.driver_championships import DriversChampionshipsRecord
from validation.records import ExportRecord
from scrapers.base.transformers import RecordTransformer


class DriversChampionshipsTransformer(RecordTransformer):
    @staticmethod
    def _parse_drivers_championships(raw: Any) -> DriversChampionshipsRecord:
        """
        Deleguje parsowanie do DriverService.parse_championships.

        Wejście (po TextColumn) bywa np.:
        - "0"
        - "2\\n2005–2006"
        - "7\\n1994–1995, 2000–2004"
        """
        return DriverService.parse_championships(raw)  # type: ignore[return-value]

    def transform(self, records: List[ExportRecord]) -> List[ExportRecord]:
        for row in records:
            champs_raw = row.get("drivers_championships")
            row["drivers_championships"] = self._parse_drivers_championships(champs_raw)
        return records


