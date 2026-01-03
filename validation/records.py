from abc import ABC, abstractmethod
from typing import Any, Callable, Mapping, Sequence
from typing import Dict
from typing import TypeAlias


ExportRecord: TypeAlias = Dict[str, Any]


class RecordValidator(ABC):
    def __init__(self, record_factory: Callable[..., Any] | type | None = None) -> None:
        self.record_factory = record_factory

    @abstractmethod
    def validate(self, record: ExportRecord) -> list[str]:
        raise NotImplementedError

    def set_record_factory(self, record_factory: Callable[..., Any] | type | None) -> None:
        self.record_factory = record_factory

    def validate_record_factory(self, record: ExportRecord) -> list[str]:
        record_factory = self.record_factory
        if record_factory is None:
            return []

        model_validate = getattr(record_factory, "model_validate", None)
        if callable(model_validate):
            try:
                model_validate(record)
            except Exception as exc:
                return [f"model_validate failed: {exc}"]
            return []

        validate_record = getattr(record_factory, "validate_record", None)
        if callable(validate_record):
            try:
                errors = validate_record(record)
            except Exception as exc:
                return [f"validate_record failed: {exc}"]
            if not errors:
                return []
            return [str(error) for error in errors]

        validate = getattr(record_factory, "validate", None)
        if callable(validate) and not isinstance(record_factory, type):
            try:
                validate()
            except Exception as exc:
                return [f"validate failed: {exc}"]
        return []

    @staticmethod
    def require_keys(record: Mapping[str, Any], keys: Sequence[str]) -> list[str]:
        return [f"Missing key: {key}" for key in keys if key not in record]

    @staticmethod
    def require_type(
        record: Mapping[str, Any],
        key: str,
        expected_types: type | tuple[type, ...],
        *,
        allow_none: bool = False,
    ) -> list[str]:
        if key not in record:
            return [f"Missing key: {key}"]
        value = record[key]
        if value is None:
            return [] if allow_none else [f"Null value for: {key}"]
        if not isinstance(value, expected_types):
            expected = (
                expected_types
                if isinstance(expected_types, tuple)
                else (expected_types,)
            )
            expected_names = ", ".join(t.__name__ for t in expected)
            return [
                f"Invalid type for {key}: expected {expected_names}, got {type(value).__name__}"
            ]
        return []

    @staticmethod
    def require_link_dict(value: Any, field_name: str) -> list[str]:
        if not isinstance(value, dict):
            return [f"{field_name} must be a link dict"]
        errors: list[str] = []
        text = value.get("text")
        if not isinstance(text, str) or not text.strip():
            errors.append(f"{field_name}.text must be a non-empty string")
        url = value.get("url")
        if url is not None and not isinstance(url, str):
            errors.append(f"{field_name}.url must be a string or None")
        return errors

    @classmethod
    def require_link_list(cls, value: Any, field_name: str) -> list[str]:
        if not isinstance(value, list):
            return [f"{field_name} must be a list of links"]
        errors: list[str] = []
        for index, item in enumerate(value):
            if not isinstance(item, dict):
                errors.append(f"{field_name}[{index}] must be a link dict")
                continue
            errors.extend(cls.require_link_dict(item, f"{field_name}[{index}]"))
        return errors
