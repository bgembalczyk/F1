from __future__ import annotations

from dataclasses import dataclass

from models.domain_model import DomainModel

from models.merge_types.constants import RecordDict


@dataclass(slots=True)
class RaceRecordModel(DomainModel):
    raw: RecordDict

    @classmethod
    def from_object(cls, value: object) -> RaceRecordModel | None:
        if not isinstance(value, dict):
            return None
        record: RecordDict = value
        return cls(raw=record)

    def to_dict(self) -> RecordDict:
        return self.raw
