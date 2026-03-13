"""Domain-level record validator with concrete field-checking helpers.

Extracted from validation/records.py to keep each module focused.
"""
from typing import Any
from typing import Sequence

from validation.issue import ValidationIssue
from validation.validator_base import RecordValidator


class BaseDomainRecordValidator(RecordValidator):
    @staticmethod
    def require_link_dict(value: Any, field_name: str) -> list[ValidationIssue]:
        if not isinstance(value, dict):
            return [ValidationIssue.custom(f"{field_name} must be a link dict")]
        errors: list[ValidationIssue] = []
        text = value.get("text")
        if not isinstance(text, str) or not text.strip():
            errors.append(
                ValidationIssue.custom(f"{field_name}.text must be a non-empty string"),
            )
        url = value.get("url")
        if url is not None and not isinstance(url, str):
            errors.append(
                ValidationIssue.custom(f"{field_name}.url must be a string or None"),
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
                    ValidationIssue.custom(f"{field_name}[{index}] must be a link dict"),
                )
                continue
            errors.extend(cls.require_link_dict(item, f"{field_name}[{index}]"))
        return errors
