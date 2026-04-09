from scrapers.base.table.columns.context import ColumnContext
from scrapers.engines import columns_engines as col


def ctx(raw_text: str, *, clean_text: str | None = None) -> ColumnContext:
    return ColumnContext(
        header="Header",
        key="key",
        raw_text=raw_text,
        clean_text=clean_text or raw_text,
        links=[],
        cell=None,
        base_url="https://en.wikipedia.org",
        model_fields=None,
    )


def test_engine_configuration_column_parse() -> None:
    column = col.EngineConfigurationColumn()
    parsed = column.parse(ctx("90° V8 + supercharger"))

    assert parsed == {
        "text": "90° V8 + supercharger",
        "max_cylinders": 8,
        "angle": {"value": 90.0, "unit": "deg"},
        "type": "V8",
        "extras": ["supercharger"],
    }


def test_fuel_limit_per_race_column_parse() -> None:
    column = col.FuelLimitPerRaceColumn()
    parsed = column.parse(ctx("Approx. 100-110 kg (90-100 L)"))

    assert parsed == {
        "has_limit": True,
        "is_estimated": True,
        "range_kg": {
            "min": {"value": 100.0, "unit": "kg"},
            "max": {"value": 110.0, "unit": "kg"},
        },
        "range_l": {
            "min": {"value": 90.0, "unit": "L"},
            "max": {"value": 100.0, "unit": "L"},
        },
    }


def test_fuel_flow_rate_column_parse() -> None:
    column = col.FuelFlowRateColumn()
    parsed = column.parse(ctx("100 kg/h above 10,500 RPM"))

    assert parsed == {
        "rate": {"value": 100.0, "unit": "kg/h"},
        "applies_above_rpm": {"value": 10500.0, "unit": "RPM"},
    }


def test_fuel_injection_pressure_limit_column_parse() -> None:
    column = col.FuelInjectionPressureLimitColumn()
    parsed = column.parse(ctx("500 bar"))

    assert parsed == {"limit": {"value": 500.0, "unit": "bar"}}


def test_engine_rpm_limit_column_parse() -> None:
    column = col.EngineRpmLimitColumn()
    parsed = column.parse(ctx("15,000"))

    assert parsed == {"limit": {"min": 15000.0, "max": 15000.0}}
