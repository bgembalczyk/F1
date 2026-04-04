from validation.composite_validator import CompositeRecordValidator
from validation.issue import ValidationIssue
from validation.pipeline import FunctionalValidator
from validation.pipeline import ValidationPipeline
from validation.pipeline import ValidationStage


def test_validation_pipeline_returns_standardized_result() -> None:
    pipeline = ValidationPipeline(
        stages=(
            ValidationStage(
                name="schema",
                validators=(
                    FunctionalValidator(
                        name="required_name",
                        handler=lambda record: (
                            []
                            if "name" in record
                            else [ValidationIssue.missing("name")]
                        ),
                    ),
                ),
            ),
        ),
    )

    invalid = pipeline.validate({})
    valid = pipeline.validate({"name": "Max"})

    assert invalid.status == "invalid"
    assert [issue.code for issue in invalid.violations] == ["missing"]
    assert valid.status == "valid"
    assert valid.violations == ()


def test_composite_validator_uses_schema_business_and_completeness_stages() -> None:
    class StubRecordFactoryValidator:
        def validate_record(self, _record):
            return [ValidationIssue.custom("factory failed", code="record_factory")]

    def business_rule(_record):
        return [ValidationIssue.custom("rule failed", code="domain")]

    validator = CompositeRecordValidator(
        common_rules=(),
        domain_rules=(business_rule,),
        record_factory_validator=StubRecordFactoryValidator(),
    )

    result = validator.validate_result({})

    assert result.status == "invalid"
    assert [issue.code for issue in result.violations] == ["domain", "record_factory"]
