"""Record validator composed from shared and domain-specific rule sets."""

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from validation.rule_engine import RuleEngine
from validation.validator_base import ExportRecord
from validation.validator_base import RecordValidator

if TYPE_CHECKING:
    from collections.abc import Sequence

    from validation.issue import ValidationIssue
    from validation.rules import ValidationRule


class CompositeRecordValidator(RecordValidator):
    def __init__(
        self,
        *,
        common_rules: Sequence[ValidationRule] = (),
        domain_rules: Sequence[ValidationRule] = (),
        record_factory: Any = None,
    ) -> None:
        super().__init__(record_factory=record_factory)
        self._common_rules = tuple(common_rules)
        self._domain_rules = tuple(domain_rules)

    def validate(self, record: ExportRecord) -> list[ValidationIssue]:
        return RuleEngine.execute(record, (*self._common_rules, *self._domain_rules))
