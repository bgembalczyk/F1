from collections.abc import Mapping
from typing import Any

from validation.issue import ValidationIssue
from validation.schemas import RecordSchema


class ValidatedModel:
    """Shared validation contract for model objects and raw records."""

    __schema__: RecordSchema | Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        return

    @classmethod
    def validate_schema(
        cls,
        record: Mapping[str, Any],
        schema: RecordSchema | Mapping[str, Any],
    ) -> list[ValidationIssue]:
        return RecordSchema.from_mapping(schema).validate(record)

    @classmethod
    def validate_record(cls, record: Mapping[str, Any]) -> list[ValidationIssue]:
        schema = cls.__schema__
        if schema is None:
            return []
        return cls.validate_schema(record, schema)

    @classmethod
    def model_validate(cls, record: Mapping[str, Any]) -> "ValidatedModel":
        errors = cls.validate_record(record)
        if errors:
            details = ", ".join(error.message for error in errors)
            msg = f"{cls.__name__} validation failed: {details}"
            raise ValueError(msg)
        return cls(**dict(record))
