from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from typing import Dict
from typing import TypeAlias

from validation.issue import ValidationIssue
from validation.quality_stats import QualityStats
from validation.schemas import NestedSchema
from validation.schemas import RecordSchema

ExportRecord: TypeAlias = Dict[str, Any]


class RecordValidator(ABC):
    def __init__(self, record_factory: Callable[..., Any] | type | None = None) -> None:
        self.record_factory = record_factory
        self._stats = QualityStats()

    @abstractmethod
    def validate(self, record: ExportRecord) -> list[ValidationIssue]:
        raise NotImplementedError

    def set_record_factory(
        self, record_factory: Callable[..., Any] | type | None
    ) -> None:
        self.record_factory = record_factory

    def reset_stats(self) -> None:
        self._stats = QualityStats()

    def record_validation_result(self, errors: Sequence[ValidationIssue | str]) -> None:
        issues = [self._coerce_issue(error) for error in errors]
        self._stats.total_records += 1
        if issues:
            self._stats.rejected_records += 1
        self._track_errors(issues)

    def _track_errors(self, errors: Sequence[ValidationIssue]) -> None:
        for error in errors:
            if error.code in {"missing", "null"} and error.field:
                self._stats.missing[error.field] = (
                    self._stats.missing.get(error.field, 0) + 1
                )
                continue
            if error.code == "type" and error.field:
                self._stats.types[error.field] = (
                    self._stats.types.get(error.field, 0) + 1
                )

    @staticmethod
    def _extract_missing_key(error: str) -> str | None:
        if error.startswith("Missing key: "):
            return error.replace("Missing key: ", "", 1).strip() or None
        if error.startswith("Null value for: "):
            return error.replace("Null value for: ", "", 1).strip() or None
        if error.endswith(" is missing"):
            return error[: -len(" is missing")].strip() or None
        return None

    @staticmethod
    def _extract_type_key(error: str) -> str | None:
        if error.startswith("Invalid type for "):
            trimmed = error.replace("Invalid type for ", "", 1)
            return trimmed.split(":", 1)[0].strip() or None
        if " must be " in error:
            return error.split(" must be ", 1)[0].strip() or None
        return None

    @classmethod
    def _coerce_issue(cls, error: ValidationIssue | str) -> ValidationIssue:
        if isinstance(error, ValidationIssue):
            return error
        message = str(error)
        missing_key = cls._extract_missing_key(message)
        if missing_key:
            code = "null" if message.startswith("Null value for: ") else "missing"
            return ValidationIssue(code=code, field=missing_key, message=message)
        type_key = cls._extract_type_key(message)
        if type_key:
            return ValidationIssue(code="type", field=type_key, message=message)
        return ValidationIssue.custom(message)

    def build_quality_report(self) -> dict[str, Any]:
        accepted = self._stats.total_records - self._stats.rejected_records
        return {
            "summary": {
                "total_records": self._stats.total_records,
                "accepted_records": accepted,
                "rejected_records": self._stats.rejected_records,
            },
            "missing": dict(sorted(self._stats.missing.items())),
            "types": dict(sorted(self._stats.types.items())),
        }

    def write_quality_report(self, debug_dir: Path) -> Path:
        debug_dir.mkdir(parents=True, exist_ok=True)
        report_path = debug_dir / "quality_report.json"
        with report_path.open("w", encoding="utf-8") as handle:
            json.dump(self.build_quality_report(), handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        return report_path

    def validate_record_factory(self, record: ExportRecord) -> list[ValidationIssue]:
        record_factory = self.record_factory
        if record_factory is None:
            return []

        model_validate = getattr(record_factory, "model_validate", None)
        if callable(model_validate):
            try:
                model_validate(record)
            except Exception as exc:
                return [
                    ValidationIssue.custom(
                        f"model_validate failed: {exc}",
                        code="record_factory",
                    )
                ]
            return []

        validate_record = getattr(record_factory, "validate_record", None)
        if callable(validate_record):
            try:
                errors = validate_record(record)
            except Exception as exc:
                return [
                    ValidationIssue.custom(
                        f"validate_record failed: {exc}",
                        code="record_factory",
                    )
                ]
            if not errors:
                return []
            return [self._coerce_issue(error) for error in errors]

        validate = getattr(record_factory, "validate", None)
        if callable(validate) and not isinstance(record_factory, type):
            try:
                validate()
            except Exception as exc:
                return [
                    ValidationIssue.custom(
                        f"validate failed: {exc}",
                        code="record_factory",
                    )
                ]
        return []

    @classmethod
    def validate_schema(
        cls, record: Mapping[str, Any], schema: RecordSchema | Mapping[str, Any]
    ) -> list[ValidationIssue]:
        normalized = cls._coerce_schema(schema)
        errors: list[ValidationIssue] = []
        errors.extend(cls.require_keys(record, normalized.required))
        allow_none = set(normalized.allow_none)
        for key, expected_types in normalized.types.items():
            errors.extend(
                cls.require_type(
                    record,
                    key,
                    expected_types,
                    allow_none=key in allow_none,
                )
            )
        for key, nested_schema in normalized.nested.items():
            if key not in record:
                continue
            value = record[key]
            if value is None:
                continue
            errors.extend(cls._validate_nested_value(key, value, nested_schema))
        for validator in normalized.custom_validators:
            errors.extend(cls._coerce_issue(error) for error in validator(record))
        return errors

    @classmethod
    def _validate_nested_value(
        cls, key: str, value: Any, nested_schema: NestedSchema
    ) -> list[ValidationIssue]:
        errors: list[ValidationIssue] = []
        if nested_schema.is_list:
            if not isinstance(value, list):
                errors.append(
                    ValidationIssue.type_error(
                        key,
                        "list",
                        type(value).__name__,
                    )
                )
                return errors
            for index, item in enumerate(value):
                if not isinstance(item, Mapping):
                    errors.append(
                        ValidationIssue.custom(f"{key}[{index}] must be a mapping")
                    )
                    continue
                errors.extend(
                    cls._prefix_errors(
                        cls._validate_nested_schema(item, nested_schema.schema),
                        f"{key}[{index}]",
                    )
                )
            return errors
        if not isinstance(value, Mapping):
            return [ValidationIssue.custom(f"{key} must be a mapping")]
        errors.extend(
            cls._prefix_errors(
                cls._validate_nested_schema(value, nested_schema.schema),
                key,
            )
        )
        return errors

    @classmethod
    def _validate_nested_schema(
        cls,
        record: Mapping[str, Any],
        nested_schema: RecordSchema
        | Callable[[Mapping[str, Any]], Sequence[ValidationIssue | str]],
    ) -> list[ValidationIssue]:
        if isinstance(nested_schema, RecordSchema):
            return cls.validate_schema(record, nested_schema)
        return [cls._coerce_issue(error) for error in nested_schema(record)]

    @staticmethod
    def _prefix_errors(
        errors: Sequence[ValidationIssue], prefix: str
    ) -> list[ValidationIssue]:
        prefixed: list[ValidationIssue] = []
        for error in errors:
            prefixed.append(error.with_prefix(prefix))
        return prefixed

    @staticmethod
    def _coerce_schema(schema: RecordSchema | Mapping[str, Any]) -> RecordSchema:
        if isinstance(schema, RecordSchema):
            return schema
        return RecordSchema(
            required=schema.get("required", ()),
            types=schema.get("types", {}),
            allow_none=schema.get("allow_none", ()),
            nested=schema.get("nested", {}),
            custom_validators=schema.get("custom_validators", ()),
        )


class BaseDomainRecordValidator(RecordValidator):
    @staticmethod
    def require_keys(
        record: Mapping[str, Any], keys: Sequence[str]
    ) -> list[ValidationIssue]:
        return [ValidationIssue.missing(key) for key in keys if key not in record]

    @staticmethod
    def require_type(
        record: Mapping[str, Any],
        key: str,
        expected_types: type | tuple[type, ...],
        *,
        allow_none: bool = False,
    ) -> list[ValidationIssue]:
        if key not in record:
            return [ValidationIssue.missing(key)]
        value = record[key]
        if value is None:
            return [] if allow_none else [ValidationIssue.null(key)]
        if not isinstance(value, expected_types):
            expected = (
                expected_types
                if isinstance(expected_types, tuple)
                else (expected_types,)
            )
            expected_names = ", ".join(t.__name__ for t in expected)
            return [
                ValidationIssue.type_error(
                    key,
                    expected_names,
                    type(value).__name__,
                )
            ]
        return []

    @staticmethod
    def require_link_dict(value: Any, field_name: str) -> list[ValidationIssue]:
        if not isinstance(value, dict):
            return [ValidationIssue.custom(f"{field_name} must be a link dict")]
        errors: list[ValidationIssue] = []
        text = value.get("text")
        if not isinstance(text, str) or not text.strip():
            errors.append(
                ValidationIssue.custom(f"{field_name}.text must be a non-empty string")
            )
        url = value.get("url")
        if url is not None and not isinstance(url, str):
            errors.append(
                ValidationIssue.custom(f"{field_name}.url must be a string or None")
            )
        return errors

    @classmethod
    def require_link_list(cls, value: Any, field_name: str) -> list[ValidationIssue]:
        if not isinstance(value, list):
            return [ValidationIssue.custom(f"{field_name} must be a list of links")]
        errors: list[ValidationIssue] = []
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                errors.append(
                    ValidationIssue.custom(f"{field_name}[{index}] must be a link dict")
                )
                continue
            errors.extend(cls.require_link_dict(item, f"{field_name}[{index}]"))
        return errors
