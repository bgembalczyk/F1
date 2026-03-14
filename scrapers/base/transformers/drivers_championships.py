from typing import Any

from models.records.driver_championships import DriversChampionshipsRecord
from models.services.driver_service import DriverService
from scrapers.base.transformers.record_transformer import RecordTransformer
from validation.records import ExportRecord


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

    def transform(self, records: list[ExportRecord]) -> list[ExportRecord]:
        for row in records:
            champs_raw = row.get("drivers_championships")
            row["drivers_championships"] = self._parse_drivers_championships(champs_raw)
        return records
