from collections.abc import Sequence
from dataclasses import dataclass
from dataclasses import field

from validation.issue import ValidationIssue


@dataclass
class QualityStats:
    total_records: int = 0
    rejected_records: int = 0
    missing: dict[str, int] = field(default_factory=dict)
    types: dict[str, int] = field(default_factory=dict)

    @property
    def accepted_records(self) -> int:
        return self.total_records - self.rejected_records

    def record_accepted(self) -> None:
        self.total_records += 1

    def record_rejected(self, issues: Sequence[ValidationIssue]) -> None:
        self.total_records += 1
        self.rejected_records += 1
        self._track_issues(issues)

    def _track_issues(self, issues: Sequence[ValidationIssue]) -> None:
        for issue in issues:
            if issue.code in {"missing", "null"} and issue.field:
                self.missing[issue.field] = self.missing.get(issue.field, 0) + 1
                continue
            if issue.code == "type" and issue.field:
                self.types[issue.field] = self.types.get(issue.field, 0) + 1
