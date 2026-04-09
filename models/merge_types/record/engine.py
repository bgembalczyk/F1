from __future__ import annotations

from dataclasses import dataclass

from models.merge_types.constants import RecordDict


@dataclass(slots=True)
class EngineRecordModel:
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> EngineRecordModel | None:
        if not isinstance(value, dict):
            return None
        record: RecordDict = value
        return cls(raw=record)

    def to_dict(self) -> RecordDict:
        return self.raw
