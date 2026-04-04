from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from validation.issue import ValidationIssue
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema
from validation.record_validation import validate_record


@dataclass(frozen=True)
class RecordDefinition:
    """Declarative metadata describing a record validation contract."""

    name: str
    required: Sequence[str] = ()
    types: Mapping[str, type | tuple[type, ...]] = field(default_factory=dict)
    allow_none: Sequence[str] = ()
    nested: Mapping[str, NestedSchema] = field(default_factory=dict)
    custom_validators: Sequence[
        Callable[[Mapping[str, Any]], Sequence[ValidationIssue | str]]
    ] = ()

    def to_schema(self) -> RecordSchema:
        return RecordSchema(
            required=self.required,
            types=self.types,
            allow_none=self.allow_none,
            nested=self.nested,
            custom_validators=self.custom_validators,
        )


def build_validator(
    definition: RecordDefinition,
) -> Callable[[dict[str, Any]], list[ValidationIssue]]:
    """Build a reusable validator function from a record definition."""

    schema = definition.to_schema()
    return lambda record: validate_record(record, schema)
