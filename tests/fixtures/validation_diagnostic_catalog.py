from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from validation.schemas import NestedSchema
from validation.schemas import RecordSchema


@dataclass(frozen=True)
class ValidationDiagnosticFixture:
    """Minimal fixture describing one diagnostic scenario (1:1 mapping)."""

    scenario: str
    record: dict[str, Any]
    schema: dict[str, Any]
    expected_code: str
    expected_message: str
    potential_cause: str


VALIDATION_DIAGNOSTIC_FIXTURES: tuple[ValidationDiagnosticFixture, ...] = (
    ValidationDiagnosticFixture(
        scenario="missing_required_key",
        record={"name": "Example"},
        schema={"required": ("name", "count")},
        expected_code="missing",
        expected_message="Missing key: count",
        potential_cause="Źródło danych pomija pole obowiązkowe dla rekordu.",
    ),
    ValidationDiagnosticFixture(
        scenario="null_not_allowed",
        record={"name": None},
        schema={"types": {"name": str}},
        expected_code="null",
        expected_message="Null value for: name",
        potential_cause="Normalizacja zamieniła wartość tekstową na null.",
    ),
    ValidationDiagnosticFixture(
        scenario="invalid_scalar_type",
        record={"laps": "58"},
        schema={"types": {"laps": int}},
        expected_code="type",
        expected_message="Invalid type for laps: expected int, got str",
        potential_cause="Parser zwrócił surowy string zamiast typu docelowego.",
    ),
    ValidationDiagnosticFixture(
        scenario="nested_missing_key",
        record={"driver": {"url": "https://example.com"}},
        schema={
            "nested": {
                "driver": NestedSchema(
                    schema=RecordSchema(required=("text",)),
                ),
            },
        },
        expected_code="missing",
        expected_message="Missing key: driver.text",
        potential_cause="Mapowanie obiektu zagnieżdżonego utraciło pole text.",
    ),
)
