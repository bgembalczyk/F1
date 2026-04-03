"""Record validator composed from shared and domain-specific rule sets."""

from __future__ import annotations

from typing import TYPE_CHECKING

from typing import Any

from validation.pipeline import FunctionalValidator
from validation.pipeline import ValidationPipeline
from validation.pipeline import ValidationResult
from validation.pipeline import ValidationStage
from validation.validator_base import ExportRecord
from validation.validator_base import RecordValidator

if TYPE_CHECKING:
    from collections.abc import Sequence
    from collections.abc import Mapping
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
        self._pipeline = ValidationPipeline(
            stages=(
                ValidationStage(
                    name="schema",
                    validators=tuple(
                        FunctionalValidator(
                            name=getattr(rule, "rule_name", type(rule).__name__),
                            handler=self._build_rule_handler(rule),
                        )
                        for rule in self._common_rules
                    ),
                ),
                ValidationStage(
                    name="business_rules",
                    validators=tuple(
                        FunctionalValidator(
                            name=getattr(rule, "rule_name", type(rule).__name__),
                            handler=self._build_rule_handler(rule),
                        )
                        for rule in self._domain_rules
                    ),
                ),
                ValidationStage(
                    name="completeness",
                    validators=(
                        FunctionalValidator(
                            name="record_factory",
                            handler=self.validate_record_factory,
                        ),
                    ),
                ),
            ),
        )

    def validate(self, record: ExportRecord) -> list[ValidationIssue]:
        return list(self.validate_result(record).violations)

    def validate_result(self, record: ExportRecord) -> ValidationResult:
        return self._pipeline.validate(record)

    def with_rules(self, *rules: ValidationRule) -> CompositeRecordValidator:
        return CompositeRecordValidator(
            common_rules=self._common_rules,
            domain_rules=(*self._domain_rules, *rules),
            record_factory_validator=self.record_factory_validator,
        )

    def describe_rules(self) -> dict[str, list[dict[str, Any]]]:
        return {
            "common_rules": [self._describe_rule(rule) for rule in self._common_rules],
            "domain_rules": [self._describe_rule(rule) for rule in self._domain_rules],
        }

    def _build_rule_handler(self, rule: ValidationRule):
        def _handler(record: Mapping[str, Any]) -> list[ValidationIssue]:
            result = rule(record)
            return [self._coerce_issue(error) for error in result]

        return _handler

    @staticmethod
    def _describe_rule(rule: ValidationRule) -> dict[str, Any]:
        rule_name = getattr(rule, "rule_name", type(rule).__name__)
        rule_params = dict(getattr(rule, "rule_params", {}))
        return {"name": rule_name, "params": rule_params}
