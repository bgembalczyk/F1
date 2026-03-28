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
