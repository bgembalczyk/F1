from validation.composite_validator import CompositeRecordValidator
from validation.issue import ValidationIssue
from validation.rules import ValueRange
from validation.rules import build_common_rules


def test_composite_record_validator_combines_common_and_domain_rules() -> None:
    common_rules = build_common_rules(
        required=("name",),
        types={"count": int},
        ranges={"count": ValueRange(min_value=0)},
    )

    def domain_rule(record):
        if record.get("name") == "bad":
            return [
                ValidationIssue.custom(
                    "Domain rule failed for name",
                    code="domain",
                    field="name",
                ),
            ]
        return []

    validator = CompositeRecordValidator(
        common_rules=common_rules,
        domain_rules=(domain_rule,),
    )

    errors = validator.validate({"name": "bad", "count": -1})

    assert [(error.code, error.field) for error in errors] == [
        ("range", "count"),
        ("domain", "name"),
    ]


def test_validation_issue_custom_supports_field_name() -> None:
    issue = ValidationIssue.custom("Invalid value", code="rule", field="points")

    assert issue.code == "rule"
    assert issue.field == "points"
    assert issue.message == "Invalid value"


def test_composite_record_validator_with_rules_returns_new_validator() -> None:
    def base_rule(record):
        if record.get("name") == "bad":
            return [
                ValidationIssue.custom(
                    "Base rule failed for name",
                    code="base",
                    field="name",
                ),
            ]
        return []

    def extra_rule(record):
        if record.get("count", 0) < 0:
            return [
                ValidationIssue.custom(
                    "Extra rule failed for count",
                    code="extra",
                    field="count",
                ),
            ]
        return []

    validator = CompositeRecordValidator(domain_rules=(base_rule,))
    extended = validator.with_rules(extra_rule)

    assert validator is not extended

    base_errors = validator.validate({"name": "bad", "count": -1})
    extended_errors = extended.validate({"name": "bad", "count": -1})

    assert [(error.code, error.field) for error in base_errors] == [
        ("base", "name"),
    ]
    assert [(error.code, error.field) for error in extended_errors] == [
        ("base", "name"),
        ("extra", "count"),
    ]
