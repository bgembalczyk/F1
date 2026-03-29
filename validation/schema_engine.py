"""Shared schema validation engine used by validator adapters."""

from __future__ import annotations

from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any

from validation.issue import ValidationIssue
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema


class SchemaValidationEngine:
    """Reusable schema helpers for nested validation and issue coercion."""

    @staticmethod
    def coerce_schema(schema: RecordSchema | Mapping[str, Any]) -> RecordSchema:
        if isinstance(schema, RecordSchema):
            return schema
        return RecordSchema(
            required=schema.get("required", ()),
            types=schema.get("types", {}),
            allow_none=schema.get("allow_none", ()),
            nested=schema.get("nested", {}),
            custom_validators=schema.get("custom_validators", ()),
        )

    @staticmethod
    def extract_missing_key(error: str) -> str | None:
        if error.startswith("Missing key: "):
            return error.replace("Missing key: ", "", 1).strip() or None
        if error.startswith("Null value for: "):
            return error.replace("Null value for: ", "", 1).strip() or None
        if error.endswith(" is missing"):
            return error[: -len(" is missing")].strip() or None
        return None

    @staticmethod
    def extract_type_key(error: str) -> str | None:
        if error.startswith("Invalid type for "):
            trimmed = error.replace("Invalid type for ", "", 1)
            return trimmed.split(":", 1)[0].strip() or None
        if " must be " in error:
            return error.split(" must be ", 1)[0].strip() or None
        return None

    @classmethod
    def coerce_issue(cls, error: ValidationIssue | str) -> ValidationIssue:
        if isinstance(error, ValidationIssue):
            return error
        message = str(error)
        missing_key = cls.extract_missing_key(message)
        if missing_key:
            code = "null" if message.startswith("Null value for: ") else "missing"
            return ValidationIssue(code=code, field=missing_key, message=message)
        type_key = cls.extract_type_key(message)
        if type_key:
            return ValidationIssue(code="type", field=type_key, message=message)
        return ValidationIssue.custom(message)

    @staticmethod
    def prefix_errors(
        errors: Sequence[ValidationIssue],
        prefix: str,
    ) -> list[ValidationIssue]:
        return [error.with_prefix(prefix) for error in errors]

    @classmethod
    def validate_nested_value(
        cls,
        key: str,
        value: Any,
        nested_schema: NestedSchema,
        schema_validator: Callable[
            [Mapping[str, Any], RecordSchema | Mapping[str, Any]],
            list[ValidationIssue],
        ],
    ) -> list[ValidationIssue]:
        errors: list[ValidationIssue] = []
        if nested_schema.is_list:
            if not isinstance(value, list):
                errors.append(
                    ValidationIssue.type_error(
                        key,
                        "list",
                        type(value).__name__,
                    ),
                )
                return errors
            for index, item in enumerate(value):
                if not isinstance(item, Mapping):
                    errors.append(
                        ValidationIssue.custom(f"{key}[{index}] must be a mapping"),
                    )
                    continue
                errors.extend(
                    cls.prefix_errors(
                        cls.validate_nested_schema(
                            item,
                            nested_schema.schema,
                            schema_validator,
                        ),
                        f"{key}[{index}]",
                    ),
                )
            return errors

        if not isinstance(value, Mapping):
            return [ValidationIssue.custom(f"{key} must be a mapping")]

        errors.extend(
            cls.prefix_errors(
                cls.validate_nested_schema(
                    value,
                    nested_schema.schema,
                    schema_validator,
                ),
                key,
            ),
        )
        return errors

    @classmethod
    def validate_nested_schema(
        cls,
        record: Mapping[str, Any],
        nested_schema: RecordSchema
        | Callable[[Mapping[str, Any]], Sequence[ValidationIssue | str]],
        schema_validator: Callable[
            [Mapping[str, Any], RecordSchema | Mapping[str, Any]],
            list[ValidationIssue],
        ],
    ) -> list[ValidationIssue]:
        if isinstance(nested_schema, RecordSchema):
            return schema_validator(record, nested_schema)
        return [cls.coerce_issue(error) for error in nested_schema(record)]
