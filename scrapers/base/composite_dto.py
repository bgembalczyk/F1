from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ListRecordDTO:
    data: dict[str, Any]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ListRecordDTO":
        return cls(data=dict(payload))

    def to_dict(self) -> dict[str, Any]:
        return dict(self.data)


@dataclass(frozen=True)
class DetailRecordDTO:
    data: dict[str, Any]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "DetailRecordDTO":
        return cls(data=dict(payload))

    def to_dict(self) -> dict[str, Any]:
        return dict(self.data)


@dataclass(frozen=True)
class CompositeRecordDTO:
    data: dict[str, Any]

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "CompositeRecordDTO":
        return cls(data=dict(payload))

    def to_dict(self) -> dict[str, Any]:
        return dict(self.data)


@dataclass(frozen=True)
class CompositeJSONBoundaryAdapter:
    """Compatibility adapter at JSON boundaries (input/output)."""

    def list_from_json(self, payload: dict[str, Any]) -> ListRecordDTO:
        return ListRecordDTO.from_dict(payload)

    def detail_from_json(self, payload: dict[str, Any]) -> DetailRecordDTO:
        return DetailRecordDTO.from_dict(payload)

    def output_to_json(self, record: CompositeRecordDTO) -> dict[str, Any]:
        return record.to_dict()
