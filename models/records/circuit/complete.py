from typing import Any

from typing_extensions import Required

from models.records.circuit.base import CircuitBaseRecord
from models.records.record_definition import RecordDefinition
from models.records.schema_fragments import compose_schema_fragments
from validation.record_validation import validate_record
from validation.schemas import NestedSchema


class CircuitCompleteRecord(CircuitBaseRecord, total=False):
    """High-detail circuit payload used by complete extractors.

    Semantics:
    - `Base` = transport envelope (technical metadata, e.g. source URL).
    - `Summary` = compact, list-level domain projection.
    - `Complete` = detail-level record that must include core domain sections.
    """

    name: Required[dict[str, Any]]
    circuit_status: Required[str]
    grands_prix: Required[list[dict[str, str | None]]]
    seasons: Required[list[dict[str, int | str]]]
    location: Required[dict[str, Any]]

    type: str | None
    direction: str | None
    grands_prix_held: int | None
    fia_grade: str
    history: list[Any]
    layouts: list[dict[str, Any]]


_circuit_link = compose_schema_fragments("link")["nested"]["link"]
_circuit_seasons = compose_schema_fragments("seasons")["nested"]["seasons"]

CIRCUIT_COMPLETE_DEFINITION = RecordDefinition(
    name="circuit_complete",
    required=("name", "circuit_status", "grands_prix", "seasons", "location"),
    types={
        "name": dict,
        "circuit_status": str,
        "grands_prix": list,
        "seasons": list,
        "location": dict,
        "url": str,
    },
    allow_none=("url",),
    nested={
        "name": _circuit_link,
        "grands_prix": NestedSchema(_circuit_link.schema, is_list=True),
        "seasons": _circuit_seasons,
    },
)

CIRCUIT_COMPLETE_SCHEMA = CIRCUIT_COMPLETE_DEFINITION.to_schema()


def validate_circuit_complete_record(record: dict[str, object]) -> list[str]:
    return [error.message for error in validate_record(record, CIRCUIT_COMPLETE_SCHEMA)]
