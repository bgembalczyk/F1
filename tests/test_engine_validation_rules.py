import re

import pytest

from models.validation.engine_regulation import EngineRegulation
from models.validation.engine_restriction import EngineRestriction
from models.validation.helpers import normalize_range_item
from models.validation.helpers import normalize_range_value
from models.validation.helpers import normalize_unit_list
from models.validation.helpers import normalize_unit_value
from models.validation.helpers import validate_status


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        pytest.param(
            {
                "seasons": [{"year": 2024}],
                "operating_principle": "  Four-stroke ",
                "maximum_displacement": {
                    "naturally_aspirated": {
                        "min": {"value": "1000", "unit": "cc"},
                        "max": {"value": 3500, "unit": "cc"},
                    },
                    "forced_induction": " Turbo ",
                },
                "configuration": {
                    "text": " V-angle ",
                    "angle": {"value": 90, "unit": "deg"},
                    "type": " V6 ",
                    "max_cylinders": "6",
                    "extras": [" DOHC ", "", 123],
                },
                "rpm_limit": {"value": "15000", "unit": "rpm"},
                "fuel_flow_limit": " 100 kg/h ",
                "fuel_composition": {"alcohol": " E10 ", "petrol": " unleaded "},
            },
            {
                "operating_principle": "Four-stroke",
                "na_min": 1000.0,
                "forced_induction": "Turbo",
                "config_text": "V-angle",
                "max_cylinders": 6,
                "extras": ["DOHC"],
                "rpm": 15000.0,
                "fuel_flow_limit": "100 kg/h",
                "fuel_alcohol": "E10",
            },
            id="happy-path-with-full-normalization",
        ),
        pytest.param(
            {
                "seasons": [{"year": 1990}],
                "maximum_displacement": {
                    "naturally_aspirated": [
                        {"value": "3000", "unit": "cc"},
                        3500,
                    ],
                    "forced_induction": [{"value": 1500, "unit": "cc"}],
                },
                "configuration": {},
            },
            {
                "operating_principle": None,
                "na_min": None,
                "forced_induction": [{"value": 1500.0, "unit": "cc"}],
                "config_text": None,
                "max_cylinders": None,
                "extras": [],
                "rpm": None,
                "fuel_flow_limit": None,
                "fuel_alcohol": None,
            },
            id="happy-path-list-branches-and-missing-optional-fields",
        ),
    ],
)
def test_engine_regulation_happy_paths(payload, expected):
    model = EngineRegulation(**payload)

    assert model.operating_principle == expected["operating_principle"]
    na_value = model.maximum_displacement.get("naturally_aspirated")
    if isinstance(na_value, dict):
        assert na_value["min"]["value"] == expected["na_min"]
    if expected["na_min"] is None:
        assert isinstance(na_value, list)
    assert (
        model.maximum_displacement.get("forced_induction")
        == expected["forced_induction"]
    )
    assert model.configuration["text"] == expected["config_text"]
    assert model.configuration.get("max_cylinders") == expected["max_cylinders"]
    assert model.configuration["extras"] == expected["extras"]
    rpm_limit = model.rpm_limit
    assert (None if rpm_limit is None else rpm_limit["value"]) == expected["rpm"]
    assert model.fuel_flow_limit == expected["fuel_flow_limit"]
    fuel_composition = model.fuel_composition or {}
    assert fuel_composition.get("alcohol") == expected["fuel_alcohol"]


@pytest.mark.parametrize(
    ("payload", "error_type", "message"),
    [
        pytest.param(
            {"maximum_displacement": "bad"},
            TypeError,
            "Pole maximum_displacement musi być słownikiem",
            id="maximum-displacement-must-be-dict",
        ),
        pytest.param(
            {"maximum_displacement": {"naturally_aspirated": {"value": 3000}}},
            TypeError,
            "Pole maximum_displacement.naturally_aspirated musi być listą",
            id="naturally-aspirated-dict-without-min-max-goes-through-list-branch",
        ),
        pytest.param(
            {
                "maximum_displacement": {
                    "forced_induction": [{"value": 1500, "unit": "cc"}, "oops"],
                },
            },
            TypeError,
            "Pole maximum_displacement.forced_induction[1] musi być"
            " słownikiem lub liczbą",
            id="forced-induction-list-item-invalid-type",
        ),
        pytest.param(
            {"configuration": "bad"},
            TypeError,
            "Pole configuration musi być słownikiem",
            id="configuration-must-be-dict",
        ),
        pytest.param(
            {"configuration": {"extras": "not-list"}},
            TypeError,
            "Pole configuration.extras musi być listą",
            id="configuration-extras-must-be-list",
        ),
        pytest.param(
            {"configuration": {"max_cylinders": "v6"}},
            ValueError,
            "Pole configuration.max_cylinders musi być liczbą",
            id="configuration-max-cylinders-invalid-number",
        ),
        pytest.param(
            {
                "maximum_displacement": {
                    "naturally_aspirated": {
                        "min": {"value": -1, "unit": "cc"},
                        "max": {"value": 1000, "unit": "cc"},
                    },
                },
            },
            ValueError,
            "Pole maximum_displacement.naturally_aspirated.min.value"
            " nie może być ujemne",
            id="conflicting-negative-range-value",
        ),
        pytest.param(
            {"fuel_composition": []},
            TypeError,
            "Pole fuel_composition musi być słownikiem",
            id="fuel-composition-must-be-dict",
        ),
    ],
)
def test_engine_regulation_validation_errors(payload, error_type, message):
    with pytest.raises(error_type, match=re.escape(message)):
        EngineRegulation(**payload)


@pytest.mark.parametrize(
    ("payload", "expected_limit_kind"),
    [
        pytest.param(
            {
                "year": [{"year": 2014}],
                "type_of_engine": [{"text": "V6 turbo", "url": None}],
                "size": {"value": "1600", "unit": "cc"},
                "fuel_limit_per_race": {
                    "range_kg": {
                        "min": {"value": 100, "unit": "kg"},
                        "max": {"value": 110, "unit": "kg"},
                    },
                },
                "fuel_flow_rate": {
                    "rate": {"value": 100, "unit": "kg/h"},
                    "applies_above_rpm": 10500,
                },
                "fuel_injection_pressure_limit": {
                    "limit": {"value": 500, "unit": "bar"},
                },
                "engine_rpm_limit": {
                    "limit": {
                        "min": {"value": 10000, "unit": "rpm"},
                        "max": {"value": 15000, "unit": "rpm"},
                    },
                },
                "power_output": {
                    "min": {"value": 600, "unit": "hp"},
                    "max": {"value": 1000, "unit": "hp"},
                },
            },
            "range",
            id="happy-path-limit-as-range",
        ),
        pytest.param(
            {
                "year": [{"year": 1989}],
                "type_of_engine": ["V12"],
                "engine_rpm_limit": {"limit": {"value": 12000, "unit": "rpm"}},
            },
            "unit",
            id="ambiguous-limit-as-unit-value",
        ),
    ],
)
def test_engine_restriction_happy_paths(payload, expected_limit_kind):
    _expected_size_cc = 1600.0
    _expected_rpm_min = 10000.0
    _expected_rpm_single = 12000.0

    model = EngineRestriction(**payload)

    assert model.year
    assert all(hasattr(item, "year") for item in model.year)
    if model.type_of_engine:
        assert model.type_of_engine[0].text
    if model.size is not None:
        assert model.size["value"] == _expected_size_cc
    if expected_limit_kind == "range":
        assert model.engine_rpm_limit["limit"]["min"]["value"] == _expected_rpm_min
    else:
        assert model.engine_rpm_limit["limit"]["value"] == _expected_rpm_single


@pytest.mark.parametrize(
    ("payload", "error_type", "message"),
    [
        pytest.param(
            {"fuel_limit_per_race": "bad"},
            TypeError,
            "Pole fuel_limit_per_race musi być słownikiem",
            id="fuel-limit-must-be-dict",
        ),
        pytest.param(
            {"fuel_flow_rate": "bad"},
            TypeError,
            "Pole fuel_flow_rate musi być słownikiem",
            id="flow-rate-must-be-dict",
        ),
        pytest.param(
            {"fuel_injection_pressure_limit": "bad"},
            TypeError,
            "Pole fuel_injection_pressure_limit musi być słownikiem",
            id="generic-limit-must-be-dict",
        ),
        pytest.param(
            {"fuel_flow_rate": {"rate": "fast"}},
            TypeError,
            "Pole fuel_flow_rate.rate musi być słownikiem lub liczbą",
            id="flow-rate-rate-invalid-type",
        ),
        pytest.param(
            {"engine_rpm_limit": {"limit": {"min": -1, "max": 1000}}},
            ValueError,
            "Pole engine_rpm_limit.limit.min.value nie może być ujemne",
            id="engine-rpm-limit-negative-min",
        ),
        pytest.param(
            {"type_of_engine": [123]},
            ValueError,
            "Pole type_of_engine musi być linkiem, słownikiem lub tekstem",
            id="type-of-engine-invalid-link-item",
        ),
    ],
)
def test_engine_restriction_validation_errors(payload, error_type, message):
    with pytest.raises(error_type, match=re.escape(message)):
        EngineRestriction(**payload)


@pytest.mark.parametrize(
    ("value", "allowed", "field_name", "expected", "error"),
    [
        pytest.param(
            " Active ",
            ["active", " retired ", "ACTIVE"],
            "status",
            "active",
            None,
            id="status-happy-path",
        ),
        pytest.param(
            "invalid",
            ["active", "retired"],
            "status",
            None,
            "Pole status musi mieć jedną z wartości: active, retired",
            id="status-invalid",
        ),
    ],
)
def test_validate_status(value, allowed, field_name, expected, error):
    if error is None:
        assert validate_status(value, allowed, field_name) == expected
    else:
        with pytest.raises(ValueError, match=re.escape(error)):
            validate_status(value, allowed, field_name)


@pytest.mark.parametrize(
    ("value", "field_name", "expected", "error_type", "error"),
    [
        pytest.param(
            {"value": "1.5", "unit": "bar"},
            "pressure",
            {"value": 1.5, "unit": "bar"},
            None,
            None,
            id="unit-value-dict",
        ),
        pytest.param(
            42,
            "pressure",
            {"value": 42.0, "unit": None},
            None,
            None,
            id="unit-value-number",
        ),
        pytest.param(
            "bad",
            "pressure",
            None,
            TypeError,
            "Pole pressure musi być słownikiem lub liczbą",
            id="unit-value-invalid",
        ),
    ],
)
def test_normalize_unit_value_cases(value, field_name, expected, error_type, error):
    if error is None:
        assert normalize_unit_value(value, field_name) == expected
    else:
        with pytest.raises(error_type, match=re.escape(error)):
            normalize_unit_value(value, field_name)


@pytest.mark.parametrize(
    ("value", "field_name", "expected", "error"),
    [
        pytest.param(None, "items", [], None, id="unit-list-none"),
        pytest.param(
            [{"value": "10", "unit": "kg"}, None, 2],
            "items",
            [{"value": 10.0, "unit": "kg"}, {"value": 2.0, "unit": None}],
            None,
            id="unit-list-happy-path",
        ),
        pytest.param(
            "bad",
            "items",
            None,
            "Pole items musi być listą",
            id="unit-list-invalid-container",
        ),
    ],
)
def test_normalize_unit_list_cases(value, field_name, expected, error):
    if error is None:
        assert normalize_unit_list(value, field_name) == expected
    else:
        with pytest.raises(TypeError, match=re.escape(error)):
            normalize_unit_list(value, field_name)


@pytest.mark.parametrize(
    ("value", "field_name", "expected", "error_type", "error"),
    [
        pytest.param(
            {"min": {"value": 10, "unit": "kg"}, "max": 20},
            "range",
            {
                "min": {"value": 10.0, "unit": "kg"},
                "max": {"value": 20.0, "unit": None},
            },
            None,
            None,
            id="range-value-happy-path",
        ),
        pytest.param(
            "bad",
            "range",
            None,
            TypeError,
            "Pole range musi być słownikiem",
            id="range-value-invalid",
        ),
    ],
)
def test_normalize_range_value_cases(value, field_name, expected, error_type, error):
    if error is None:
        assert normalize_range_value(value, field_name) == expected
    else:
        with pytest.raises(error_type, match=re.escape(error)):
            normalize_range_value(value, field_name)


@pytest.mark.parametrize(
    ("value", "field_name", "expected", "error"),
    [
        pytest.param(
            {"value": 1, "unit": "kg"},
            "item",
            {"value": 1.0, "unit": "kg"},
            None,
            id="range-item-dict-with-unit",
        ),
        pytest.param(
            {"value": 1},
            "item",
            {"value": 1.0, "unit": None},
            None,
            id="range-item-dict-without-unit-elif-branch",
        ),
        pytest.param(
            2,
            "item",
            {"value": 2.0, "unit": None},
            None,
            id="range-item-number",
        ),
        pytest.param(
            "bad",
            "item",
            None,
            "Pole item ma nieprawidłowy typ",
            id="range-item-invalid",
        ),
    ],
)
def test_normalize_range_item_cases(value, field_name, expected, error):
    if error is None:
        assert normalize_range_item(value, field_name) == expected
    else:
        with pytest.raises(ValueError, match=re.escape(error)):
            normalize_range_item(value, field_name)
