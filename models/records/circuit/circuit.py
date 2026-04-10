from typing import Literal
from typing import TypedDict

from models.records.record_definition import RecordDefinition
from models.records.schema_fragments import compose_schema_fragments
from validation.record_validation import validate_record
from validation.schemas import NestedSchema


class CircuitSummaryRecord(TypedDict):
    """Summary-level, list-oriented circuit projection used in core datasets."""
    circuit: dict[str, str | None]
    circuit_status: Literal["current", "future", "former"]
    type: str | None
    direction: str | None
    location: str | None
    country: str | dict[str, str | None] | None
    last_length_used_km: float | None
    last_length_used_mi: float | None
    turns: int | None
    grands_prix: list[dict[str, str | None]]
    seasons: list[dict[str, int | str]]
    grands_prix_held: int | None


CircuitRecord = CircuitSummaryRecord

_circuit_link = compose_schema_fragments("link")["nested"]["link"]
_circuit_seasons = compose_schema_fragments("seasons")["nested"]["seasons"]

CIRCUIT_SUMMARY_DEFINITION = RecordDefinition(
    name="circuit_summary",
    required=("circuit", "circuit_status", "country", "seasons"),
    types={
        "circuit": dict,
        "circuit_status": str,
        "country": (str, dict),
        "seasons": list,
        "grands_prix": list,
    },
    allow_none=("grands_prix",),
    nested={
        "circuit": _circuit_link,
        "grands_prix": NestedSchema(_circuit_link.schema, is_list=True),
        "seasons": _circuit_seasons,
    },
)

CIRCUIT_SCHEMA = CIRCUIT_SUMMARY_DEFINITION.to_schema()


def validate_circuit_record(record: dict[str, object]) -> list[str]:
    return [error.message for error in validate_record(record, CIRCUIT_SCHEMA)]
