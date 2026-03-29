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
    from validation.rules import LegacyValidationRule
    from validation.rules import ValidationRule

from validation.rules import adapt_legacy_rule


class CompositeRecordValidator(RecordValidator):
    def __init__(
        self,
        *,
        common_rules: Sequence[LegacyValidationRule] = (),
        domain_rules: Sequence[LegacyValidationRule] = (),
        record_factory_validator: RecordFactoryValidatorProtocol | None = None,
    ) -> None:
        super().__init__(record_factory_validator=record_factory_validator)
        self._common_rules = tuple(adapt_legacy_rule(rule) for rule in common_rules)
        self._domain_rules = tuple(adapt_legacy_rule(rule) for rule in domain_rules)

    def validate(self, record: ExportRecord) -> list[ValidationIssue]:
        return self._execute_rules(record, (*self._common_rules, *self._domain_rules))

    @classmethod
    def _execute_rules(
        cls,
        record: Mapping[str, Any],
        rules: Sequence[ValidationRule],
    ) -> list[ValidationIssue]:
        errors: list[ValidationIssue] = []
        for rule in rules:
            errors.extend(rule(record))
        return errors
