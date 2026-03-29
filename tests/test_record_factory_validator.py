from validation.record_factory_validator import (
    ModelValidateRecordFactoryValidatorAdapter,
)
from validation.record_factory_validator import (
    ValidateMethodRecordFactoryValidatorAdapter,
)
from validation.record_factory_validator import ValidateRecordFactoryValidatorAdapter
from validation.record_factory_validator import adapt_record_factory_validator
from validation.validator_base import RecordValidator


class DummyValidator(RecordValidator):
    def validate(self, _record):  # type: ignore[override]
        return []


def test_adapt_record_factory_validator_supports_model_validate() -> None:
    class Factory:
        @staticmethod
        def model_validate(_record):
            return object()

    adapter = adapt_record_factory_validator(Factory)

    assert isinstance(adapter, ModelValidateRecordFactoryValidatorAdapter)


def test_adapt_record_factory_validator_supports_validate_record() -> None:
    class Factory:
        @staticmethod
        def validate_record(_record):
            return ["Missing key: name"]

    adapter = adapt_record_factory_validator(Factory)

    assert isinstance(adapter, ValidateRecordFactoryValidatorAdapter)


def test_adapt_record_factory_validator_supports_validate() -> None:
    class Factory:
        def validate(self):
            return None

    adapter = adapt_record_factory_validator(Factory())

    assert isinstance(adapter, ValidateMethodRecordFactoryValidatorAdapter)


def test_validate_record_factory_coerces_errors_from_adapter() -> None:
    class Factory:
        @staticmethod
        def validate_record(_record):
            return ["Missing key: name"]

    validator = DummyValidator(
        record_factory_validator=adapt_record_factory_validator(Factory),
    )

    errors = validator.validate_record_factory({"driver": "Max"})

    assert len(errors) == 1
    assert errors[0].code == "missing"
    assert errors[0].field == "name"


def test_validate_record_factory_handles_exceptions_in_one_place() -> None:
    class Factory:
        @staticmethod
        def validate_record(_record):
            msg = "broken"
            raise ValueError(msg)

    validator = DummyValidator(
        record_factory_validator=adapt_record_factory_validator(Factory),
    )

    errors = validator.validate_record_factory({})

    assert len(errors) == 1
    assert errors[0].code == "record_factory"
    assert errors[0].message == "record factory validation failed: broken"
