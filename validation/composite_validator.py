"""Record validator composed from shared and domain-specific rule sets."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from validation.validator_base import ExportRecord
from validation.validator_base import RecordValidator

if TYPE_CHECKING:
    from collections.abc import Mapping
    from collections.abc import Sequence

    from validation.issue import ValidationIssue
    from validation.record_factory_validator import RecordFactoryValidatorProtocol
    from validation.rules import ValidationRule


class CompositeRecordValidator(RecordValidator):
    def __init__(
        self,
        *,
        common_rules: Sequence[ValidationRule] = (),
        domain_rules: Sequence[ValidationRule] = (),
        record_factory_validator: RecordFactoryValidatorProtocol | None = None,
    ) -> None:
        super().__init__(record_factory_validator=record_factory_validator)
        self._common_rules = tuple(common_rules)
        self._domain_rules = tuple(domain_rules)

    def validate(self, record: ExportRecord) -> list[ValidationIssue]:
        return self._execute_rules(record, (*self._common_rules, *self._domain_rules))

    def describe_rules(self) -> dict[str, list[dict[str, Any]]]:
        return {
            "common_rules": [self._describe_rule(rule) for rule in self._common_rules],
            "domain_rules": [self._describe_rule(rule) for rule in self._domain_rules],
        }

    @classmethod
    def _execute_rules(
        cls,
        record: Mapping[str, Any],
        rules: Sequence[ValidationRule],
    ) -> list[ValidationIssue]:
        errors: list[ValidationIssue] = []
        for rule in rules:
            result = rule(record)
            errors.extend(cls._coerce_issue(error) for error in result)
        return errors

    @staticmethod
    def _describe_rule(rule: ValidationRule) -> dict[str, Any]:
        rule_name = getattr(rule, "rule_name", type(rule).__name__)
        rule_params = dict(getattr(rule, "rule_params", {}))
        return {"name": rule_name, "params": rule_params}
