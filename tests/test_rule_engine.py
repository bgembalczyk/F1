from validation.issue import ValidationIssue
from validation.rule_engine import RuleEngine


def test_rule_engine_execute_coerces_rule_errors() -> None:
    def invalid_type_rule(record):
        del record
        return ["Invalid type for points: expected int, got str"]

    def domain_rule(record):
        del record
        return [ValidationIssue.custom("Rule failed", code="domain", field="name")]

    errors = RuleEngine.execute({}, (invalid_type_rule, domain_rule))

    assert [(error.code, error.field) for error in errors] == [
        ("type", "points"),
        ("domain", "name"),
    ]


def test_rule_engine_coerce_issue_recognizes_missing_and_null_keys() -> None:
    missing = RuleEngine.coerce_issue("Missing key: season")
    null = RuleEngine.coerce_issue("Null value for: season")

    assert (missing.code, missing.field) == ("missing", "season")
    assert (null.code, null.field) == ("null", "season")
