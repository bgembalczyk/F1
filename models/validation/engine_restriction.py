from dataclasses import dataclass, field
from typing import Any, Dict, List

from models.validation.base import ValidatedModel
from models.validation.helpers import normalize_range_value
from models.validation.helpers import normalize_unit_value
from models.validation.validators import normalize_link_list, normalize_season_list
from models.value_objects.link import Link
from models.value_objects.season_ref import SeasonRef


@dataclass
class EngineRestriction(ValidatedModel):
    year: List[SeasonRef | dict[str, Any]] = field(default_factory=list)
    size: Dict[str, Any] | None = None
    type_of_engine: List[Link | dict[str, Any]] = field(default_factory=list)
    fuel_limit_per_race: Dict[str, Any] | None = None
    fuel_flow_rate: Dict[str, Any] | None = None
    fuel_injection_pressure_limit: Dict[str, Any] | None = None
    engine_rpm_limit: Dict[str, Any] | None = None
    power_output: Dict[str, Any] | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.year = normalize_season_list(self.year)
        self.type_of_engine = normalize_link_list(self.type_of_engine)
        self.size = normalize_unit_value(self.size, "size")
        self.fuel_limit_per_race = self._normalize_fuel_limit(self.fuel_limit_per_race)
        self.fuel_flow_rate = self._normalize_flow_rate(self.fuel_flow_rate)
        self.fuel_injection_pressure_limit = self._normalize_limit(
            self.fuel_injection_pressure_limit, "fuel_injection_pressure_limit",
        )
        self.engine_rpm_limit = self._normalize_limit(
            self.engine_rpm_limit, "engine_rpm_limit", range_key="limit",
        )
        self.power_output = normalize_range_value(self.power_output, "power_output")

    @staticmethod
    def _normalize_fuel_limit(value: Dict[str, Any] | None) -> Dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("Pole fuel_limit_per_race musi być słownikiem")
        result: Dict[str, Any] = dict(value)
        if "range_kg" in result:
            result["range_kg"] = normalize_range_value(
                result.get("range_kg"), "fuel_limit_per_race.range_kg",
            )
        if "range_l" in result:
            result["range_l"] = normalize_range_value(
                result.get("range_l"), "fuel_limit_per_race.range_l",
            )
        return result

    @staticmethod
    def _normalize_flow_rate(value: Dict[str, Any] | None) -> Dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("Pole fuel_flow_rate musi być słownikiem")
        result: Dict[str, Any] = dict(value)
        if "rate" in result:
            result["rate"] = normalize_unit_value(
                result.get("rate"), "fuel_flow_rate.rate",
            )
        if "applies_above_rpm" in result:
            result["applies_above_rpm"] = normalize_unit_value(
                result.get("applies_above_rpm"), "fuel_flow_rate.applies_above_rpm",
            )
        return result

    @staticmethod
    def _normalize_limit(
            value: Dict[str, Any] | None,
            field_name: str,
            *,
            range_key: str | None = None,
    ) -> Dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError(f"Pole {field_name} musi być słownikiem")
        result: Dict[str, Any] = dict(value)
        key = range_key or "limit"
        if key in result:
            limit_value = result.get(key)
            if isinstance(limit_value, dict) and "min" in limit_value:
                result[key] = normalize_range_value(limit_value, f"{field_name}.{key}")
            else:
                result[key] = normalize_unit_value(limit_value, f"{field_name}.{key}")
        return result
