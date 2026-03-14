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
    def custom(cls, message: str, *, code: str = "custom") -> "ValidationIssue":
        return cls(code=code, message=message)

    def with_prefix(self, prefix: str) -> "ValidationIssue":
        if self.code in {"missing", "null", "type"} and self.field:
            new_field = f"{prefix}.{self.field}"
            if self.code == "missing":
                return ValidationIssue.missing(new_field)
            if self.code == "null":
                return ValidationIssue.null(new_field)
            message = self.message
            if message:
                token = f"Invalid type for {self.field}"
                if message.startswith(token):
                    message = message.replace(
                        token,
                        f"Invalid type for {new_field}",
                        1,
                    )
            else:
                message = f"Invalid type for {new_field}"
            return ValidationIssue(code="type", field=new_field, message=message)

        message = self.message
        message = f"{prefix}.{message}" if message else prefix
        return ValidationIssue(code=self.code, message=message)
