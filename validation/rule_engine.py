"""Execution engine for composable validation rules."""

from __future__ import annotations

from collections.abc import Mapping
from collections.abc import Sequence
from typing import Any

from validation.issue import ValidationIssue
from validation.rules import ValidationRule


class RuleEngine:
    """Runs rule pipelines and normalizes rule output into ``ValidationIssue``."""

    @classmethod
    def execute(
        cls,
        record: Mapping[str, Any],
        rules: Sequence[ValidationRule],
    ) -> list[ValidationIssue]:
        errors: list[ValidationIssue] = []
        for rule in rules:
            result = rule(record)
            errors.extend(cls.coerce_issue(error) for error in result)
        return errors

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
    def coerce_issue(cls, error: ValidationIssue | str) -> ValidationIssue:
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
