from __future__ import annotations

from dataclasses import dataclass

from models.merge_types.constants import RecordDict


@dataclass(slots=True)
class SeasonRecordModel:
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> SeasonRecordModel | None:
        if not isinstance(value, dict):
            return None
        record: RecordDict = value
        return cls(raw=record)

    def year(self) -> int | None:
        year = self.raw.get("year")
        if isinstance(year, int):
            return year
        return None

    def append_livery(self, livery_payload: RecordDict) -> None:
        existing_liveries = self.raw.get("liveries")
        if isinstance(existing_liveries, list):
            existing_liveries.append(livery_payload)
            return
        existing_livery = self.raw.pop("livery", None)
        season_liveries: list[object] = []
        if existing_livery is not None:
            season_liveries.append(existing_livery)
        season_liveries.append(livery_payload)
        self.raw["liveries"] = season_liveries
