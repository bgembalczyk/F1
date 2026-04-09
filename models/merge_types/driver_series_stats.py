from __future__ import annotations

from dataclasses import dataclass

from models.merge_types.constants import RecordDict


@dataclass(frozen=True, slots=True)
class DriverSeriesStats:
    race_entries: object | None
    race_starts: object | None
    extras: RecordDict

    @classmethod
    def from_dict(cls, payload: RecordDict) -> DriverSeriesStats:
        race_entries = payload.get("race_entries")
        if race_entries is None:
            race_entries = payload.get("entries")
        race_starts = payload.get("race_starts")
        if race_starts is None:
            race_starts = payload.get("starts")
        extras = {
            key: value
            for key, value in payload.items()
            if key not in {"race_entries", "entries", "race_starts", "starts"}
        }
        return cls(race_entries=race_entries, race_starts=race_starts, extras=extras)

    def to_dict(self) -> RecordDict:
        payload = dict(self.extras)
        if self.race_entries is not None:
            payload["race_entries"] = self.race_entries
        if self.race_starts is not None:
            payload["race_starts"] = self.race_starts
        return payload
