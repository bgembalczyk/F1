from tests.fixtures.validation_diagnostic_catalog import VALIDATION_DIAGNOSTIC_FIXTURES
from validation.record_validation import validate_record


def test_validation_fixture_catalog_is_one_to_one_and_minimal() -> None:
    scenarios = [fixture.scenario for fixture in VALIDATION_DIAGNOSTIC_FIXTURES]
    assert len(scenarios) == len(set(scenarios))

    for fixture in VALIDATION_DIAGNOSTIC_FIXTURES:
        assert fixture.record, f"Pusty rekord dla scenariusza: {fixture.scenario}"
        assert fixture.expected_message
        assert fixture.potential_cause


def test_validation_fixture_catalog_drives_diagnostic_scenarios() -> None:
    for fixture in VALIDATION_DIAGNOSTIC_FIXTURES:
        errors = validate_record(fixture.record, fixture.schema)

        assert len(errors) == 1, (
            f"Scenariusz={fixture.scenario} powinien mapować 1:1 na jeden wynik "
            f"diagnostyczny; potencjalna przyczyna: {fixture.potential_cause}"
        )
        assert errors[0].code == fixture.expected_code
        assert errors[0].message == fixture.expected_message
