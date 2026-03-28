from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from typing import Any

from validation.issue import ValidationIssue


@dataclass(frozen=True)
class NestedSchema:
    schema: (
        "RecordSchema | Callable[[Mapping[str, Any]], Sequence[ValidationIssue | str]]"
    )
    is_list: bool = False


@dataclass(frozen=True)
class RecordSchema:
    required: Sequence[str] = ()
    types: Mapping[str, type | tuple[type, ...]] = field(default_factory=dict)
    allow_none: Sequence[str] = ()
    nested: Mapping[str, NestedSchema] = field(default_factory=dict)
    custom_validators: Sequence[
        Callable[[Mapping[str, Any]], Sequence[ValidationIssue | str]]
    ] = ()
