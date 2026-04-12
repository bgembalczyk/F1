from typing import Any

from scrapers.parsers.wiki.table.base import WikiTableBaseMapper


class EngineRegulationTableMapper(WikiTableBaseMapper):
    table_type = "engine_regulation_progression"
    missing_columns_policy = "ignore"
    extra_columns_policy = "ignore"

    _column_mapping = {
        "Years": "seasons",
        "Operating principle": "operating_principle",
        "Maximum displacement - Naturally aspirated": "maximum_displacement",
        "Maximum displacement - Forced induction": "maximum_displacement",
        "Configuration": "configuration",
        "RPM limit": "rpm_limit",
        "Fuel flow limit (Qmax)": "fuel_flow_limit",
        "Fuel composition - Alcohol": "fuel_composition",
        "Fuel composition - Petrol": "fuel_composition",
    }

    def matches(self, headers: list[str], _table_data: dict[str, Any]) -> bool:
        required_headers = {"Years", "Operating principle", "Configuration"}
        return required_headers.issubset(set(headers))

    def map_columns(self, headers: list[str]) -> dict[str, str]:
        return {
            header: self._column_mapping[header]
            for header in headers
            if header in self._column_mapping
        }
