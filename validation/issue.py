from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str = ""
    field: str | None = None
    expected: str | None = None
    actual: str | None = None
    path_segments: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        normalized_segments = self.path_segments
        if not normalized_segments and self.field:
            normalized_segments = (self.field,)
        if normalized_segments and self.field != normalized_segments[-1]:
            object.__setattr__(self, "field", normalized_segments[-1])
        if normalized_segments != self.path_segments:
            object.__setattr__(self, "path_segments", normalized_segments)

    @property
    def path(self) -> str | None:
        if not self.path_segments:
            return None
        return ".".join(self.path_segments)

    @classmethod
    def missing(cls, field: str) -> ValidationIssue:
        issue = cls(code="missing", field=field)
        return IssueMessageFormatter.render(issue)

    @classmethod
    def null(cls, field: str) -> ValidationIssue:
        issue = cls(code="null", field=field)
        return IssueMessageFormatter.render(issue)

    @classmethod
    def type_error(cls, field: str, expected: str, actual: str) -> ValidationIssue:
        issue = cls(code="type", field=field, expected=expected, actual=actual)
        return IssueMessageFormatter.render(issue)

    @classmethod
    def custom(
        cls,
        message: str,
        *,
        code: str = "custom",
        field: str | None = None,
        expected: str | None = None,
        actual: str | None = None,
        path_segments: tuple[str, ...] = (),
    ) -> ValidationIssue:
        issue = cls(
            code=code,
            message=message,
            field=field,
            expected=expected,
            actual=actual,
            path_segments=path_segments,
        )
        return IssueMessageFormatter.render(issue)

    def with_prefix(self, prefix: str) -> ValidationIssue:
        prefix_segments = tuple(segment for segment in prefix.split(".") if segment)
        if not prefix_segments:
            return self

        existing = self.path_segments or ((self.field,) if self.field else ())
        merged = (*prefix_segments, *existing)
        return replace(self, field=merged[-1], path_segments=merged)


class IssueMessageFormatter:
    """Renders end-user messages from structured issues."""

    @staticmethod
    def format(issue: ValidationIssue) -> str:
        path = issue.path or issue.field
        if issue.code == "missing" and path:
            return f"Missing key: {path}"
        if issue.code == "null" and path:
            return f"Null value for: {path}"
        if issue.code == "type" and path and issue.expected and issue.actual:
            return (
                f"Invalid type for {path}: expected {issue.expected}, "
                f"got {issue.actual}"
            )
        return issue.message

    @classmethod
    def render(cls, issue: ValidationIssue) -> ValidationIssue:
        formatted_message = cls.format(issue)
        if issue.message == formatted_message:
            return issue
        return replace(issue, message=formatted_message)


class LegacyValidationIssueAdapter:
    """Adapter converting legacy string issues to structured ValidationIssue."""

    @staticmethod
    def from_legacy_message(error: str) -> ValidationIssue:
        message = str(error)
        if message.startswith("Missing key: "):
            path = message.replace("Missing key: ", "", 1).strip()
            return ValidationIssue.missing(path)
        if message.startswith("Null value for: "):
            path = message.replace("Null value for: ", "", 1).strip()
            return ValidationIssue.null(path)
        if message.startswith("Invalid type for ") and ":" in message:
            trimmed = message.replace("Invalid type for ", "", 1)
            path, _, details = trimmed.partition(":")
            expected = None
            actual = None
            if "expected " in details and ", got " in details:
                _, _, expected_actual = details.partition("expected ")
                expected, _, actual = expected_actual.partition(", got ")
            return ValidationIssue(
                code="type",
                field=path.strip() or None,
                expected=(expected or "").strip() or None,
                actual=(actual or "").strip() or None,
                message=message,
            )
        if message.endswith(" is missing"):
            path = message[: -len(" is missing")].strip()
            return ValidationIssue.missing(path)
        if " must be " in message:
            field = message.split(" must be ", 1)[0].strip() or None
            return ValidationIssue(code="type", field=field, message=message)
        return ValidationIssue.custom(message)
