from collections.abc import Callable
from collections.abc import Mapping
from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field
from typing import TYPE_CHECKING
from typing import Any

from validation.issue import ValidationIssue

if TYPE_CHECKING:
    from validation.rules import ValidationRule


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

    @classmethod
    def from_mapping(cls, schema: "RecordSchema | Mapping[str, Any]") -> "RecordSchema":
        if isinstance(schema, cls):
            return schema
        return cls(
            required=schema.get("required", ()),
            types=schema.get("types", {}),
            allow_none=schema.get("allow_none", ()),
            nested=schema.get("nested", {}),
            custom_validators=schema.get("custom_validators", ()),
        )

    def validate(self, record: Mapping[str, Any]) -> list[ValidationIssue]:
        from validation.validator_base import RecordValidator  # noqa: PLC0415

        errors: list[ValidationIssue] = []
        errors.extend(RecordValidator.require_keys(record, self.required))
        allow_none = set(self.allow_none)
        for key, expected_types in self.types.items():
            errors.extend(
                RecordValidator.require_type(
                    record,
                    key,
                    expected_types,
                    allow_none=key in allow_none,
                ),
            )
        for rule in self.to_rules():
            errors.extend(
                RecordValidator._coerce_issue(error)  # noqa: SLF001
                for error in rule(record)
            )
        return errors

    def to_rules(self) -> list["ValidationRule"]:
        from validation.validator_base import RecordValidator  # noqa: PLC0415

        def _nested_rule(record: Mapping[str, Any]) -> list[ValidationIssue]:
            errors: list[ValidationIssue] = []
            for key, nested_schema in self.nested.items():
                if key not in record:
                    continue
                value = record[key]
                if value is None:
                    continue
                errors.extend(
                    self._validate_nested_field(
                        key=key,
                        value=value,
                        nested_schema=nested_schema,
                    ),
                )
            return errors

        def _custom_rule(record: Mapping[str, Any]) -> list[ValidationIssue]:
            errors: list[ValidationIssue] = []
            for validator in self.custom_validators:
                errors.extend(
                    RecordValidator._coerce_issue(error) for error in validator(record)  # noqa: SLF001
                )
            return errors

        return [_nested_rule, _custom_rule]

    def _validate_nested_field(
        self,
        key: str,
        value: Any,
        nested_schema: NestedSchema,
    ) -> list[ValidationIssue]:
        from validation.validator_base import RecordValidator  # noqa: PLC0415

        errors: list[ValidationIssue] = []
        if nested_schema.is_list:
            if not isinstance(value, list):
                return [ValidationIssue.type_error(key, "list", type(value).__name__)]
            for index, item in enumerate(value):
                if not isinstance(item, Mapping):
                    errors.append(
                        ValidationIssue.custom(f"{key}[{index}] must be a mapping"),
                    )
                    continue
                errors.extend(
                    RecordValidator.prefix_errors(
                        self._validate_nested_schema(item, nested_schema.schema),
                        f"{key}[{index}]",
                    ),
                )
            return errors
        if not isinstance(value, Mapping):
            return [ValidationIssue.custom(f"{key} must be a mapping")]
        return RecordValidator.prefix_errors(
            self._validate_nested_schema(value, nested_schema.schema),
            key,
        )

    def _validate_nested_schema(
        self,
        record: Mapping[str, Any],
        nested_schema: (
            "RecordSchema"
            " | Callable[[Mapping[str, Any]], Sequence[ValidationIssue | str]]"
        ),
    ) -> list[ValidationIssue]:
        from validation.validator_base import RecordValidator  # noqa: PLC0415

        if isinstance(nested_schema, RecordSchema):
            return nested_schema.validate(record)
        return [
            RecordValidator._coerce_issue(error)  # noqa: SLF001
            for error in nested_schema(record)
        ]
