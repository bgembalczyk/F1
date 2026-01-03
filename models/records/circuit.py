from typing import Any, Literal, TypedDict

from scrapers.base.validation import RecordValidator

from models.records.link import LinkRecord
from models.records.season import SeasonRecord


class CircuitRecord(TypedDict, total=False):
    circuit: LinkRecord
    circuit_status: Literal["current", "future", "former"]
    type: str | None
    direction: str | None
    location: str | None
    country: str | None
    last_length_used_km: float | None
    last_length_used_mi: float | None
    turns: int | None
    grands_prix: list[LinkRecord]
    seasons: list[SeasonRecord]
    grands_prix_held: int | None

    @classmethod
    def validate_record(cls, record: dict[str, Any]) -> list[str]:
        errors: list[str] = []
        errors.extend(
            RecordValidator.require_keys(
                record,
                ["circuit", "circuit_status", "country", "seasons"],
            )
        )
        errors.extend(RecordValidator.require_type(record, "circuit", dict))
        errors.extend(RecordValidator.require_type(record, "circuit_status", str))
        errors.extend(RecordValidator.require_type(record, "country", (str, dict)))
        errors.extend(RecordValidator.require_type(record, "seasons", list))
        errors.extend(
            RecordValidator.require_type(record, "grands_prix", list, allow_none=True)
        )

        circuit = record.get("circuit")
        if isinstance(circuit, dict):
            errors.extend(RecordValidator.require_link_dict(circuit, "circuit"))

        grands_prix = record.get("grands_prix")
        if isinstance(grands_prix, list):
            errors.extend(RecordValidator.require_link_list(grands_prix, "grands_prix"))

        return errors
