from dataclasses import dataclass


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    field: str | None = None

    @classmethod
    def missing(cls, field: str) -> "ValidationIssue":
        return cls(code="missing", field=field, message=f"Missing key: {field}")

    @classmethod
    def null(cls, field: str) -> "ValidationIssue":
        return cls(code="null", field=field, message=f"Null value for: {field}")

    @classmethod
    def type_error(cls, field: str, expected: str, actual: str) -> "ValidationIssue":
        return cls(
            code="type",
            field=field,
            message=f"Invalid type for {field}: expected {expected}, got {actual}",
        )

    @classmethod
    def custom(
        cls,
        message: str,
        *,
        code: str = "custom",
        field: str | None = None,
    ) -> "ValidationIssue":
        return cls(code=code, field=field, message=message)

    def with_prefix(self, prefix: str) -> "ValidationIssue":
        if self.field:
            field = f"{prefix}.{self.field}"
            if self.code == "missing":
                return ValidationIssue.missing(field)
            if self.code == "null":
                return ValidationIssue.null(field)
            if self.code == "type":
                message = self.message
                token = f"Invalid type for {self.field}"
                if message.startswith(token):
                    message = message.replace(token, f"Invalid type for {field}", 1)
                return ValidationIssue(code="type", field=field, message=message)
            return ValidationIssue(code=self.code, field=field, message=self.message)

        message = self.message
        message = f"{prefix}.{message}" if message else prefix
        return ValidationIssue(code=self.code, message=message)
