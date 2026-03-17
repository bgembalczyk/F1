from scrapers.base.table.columns.types.float import FloatColumn
from scrapers.base.table.columns.types.links_list import LinksListColumn
from scrapers.base.table.columns.types.range import RangeColumn
from scrapers.base.table.columns.types.seasons import SeasonsColumn
from scrapers.base.table.columns.types.text import TextColumn
from scrapers.base.table.columns.types.unit import UnitColumn
from scrapers.base.table.dsl.column import column
from scrapers.base.table.dsl.table_schema import TableSchemaDSL
from scrapers.base.table.presets import BASE_STATS_COLUMNS
from scrapers.base.table.presets import BASE_STATS_MAP
from scrapers.engines.columns.configuration import EngineConfigurationColumn
from scrapers.engines.columns.engine_rpm_limit import EngineRpmLimitColumn
from scrapers.engines.columns.fuel_flow_rate import FuelFlowRateColumn
from scrapers.engines.columns.fuel_injection_pressure_limit import FuelInjectionPressureLimitColumn
from scrapers.engines.columns.fuel_limit_per_race import FuelLimitPerRaceColumn
from scrapers.engines.columns.manufacturer_name_status import EngineManufacturerNameStatusColumn
from scrapers.engines.columns.nested_text import NestedTextColumn
from scrapers.engines.columns.nested_unit_list import NestedUnitListColumn


def build_engine_manufacturers_schema() -> TableSchemaDSL:
    columns = [
        column("Manufacturer", "manufacturer", EngineManufacturerNameStatusColumn()),
        column("Engines built in", "engines_built_in", LinksListColumn()),
    ]
    columns += [
        column(
            header,
            key,
            FloatColumn() if key == "points" else BASE_STATS_COLUMNS[key],
        )
        for header, key in BASE_STATS_MAP.items()
    ]
    return TableSchemaDSL(columns=columns)


def build_engine_regulation_schema() -> TableSchemaDSL:
    return TableSchemaDSL(
        columns=[
            column("Years", "seasons", SeasonsColumn()),
            column("Operating principle", "operating_principle", TextColumn()),
            column(
                "Maximum displacement - Naturally aspirated",
                "maximum_displacement",
                NestedUnitListColumn("naturally_aspirated"),
            ),
            column(
                "Maximum displacement - Forced induction",
                "maximum_displacement",
                NestedUnitListColumn("forced_induction"),
            ),
            column("Configuration", "configuration", EngineConfigurationColumn()),
            column("RPM limit", "rpm_limit", UnitColumn(unit="rpm")),
            column("Fuel flow limit (Qmax)", "fuel_flow_limit", TextColumn()),
            column(
                "Fuel composition - Alcohol",
                "fuel_composition",
                NestedTextColumn("alcohol"),
            ),
            column(
                "Fuel composition - Petrol",
                "fuel_composition",
                NestedTextColumn("petrol"),
            ),
        ],
    )


def build_engine_restrictions_schema() -> TableSchemaDSL:
    return TableSchemaDSL(
        columns=[
            column("Year", "year", SeasonsColumn()),
            column("Size", "size", UnitColumn(unit="litre")),
            column("Type of engine", "type_of_engine", LinksListColumn()),
            column("Fuel-limit per race", "fuel_limit_per_race", FuelLimitPerRaceColumn()),
            column("Fuel-flow rate", "fuel_flow_rate", FuelFlowRateColumn()),
            column(
                "Fuel-injection pressure limit",
                "fuel_injection_pressure_limit",
                FuelInjectionPressureLimitColumn(),
            ),
            column("Engine RPM limit", "engine_rpm_limit", EngineRpmLimitColumn()),
            column(
                "Power Output",
                "power_output",
                RangeColumn(UnitColumn(unit="hp"), UnitColumn(unit="hp"), shared_suffix="hp"),
            ),
        ],
    )
