from dataclasses import dataclass
from dataclasses import field
from typing import Any

from models.domain_utils.normalization import normalize_link_items
from models.domain_utils.normalization import (
    normalize_season_items as core_normalize_season_items,
)
from models.validation.base import ValidatedModel
from models.validation.helpers import normalize_range_value
from models.validation.helpers import normalize_unit_value
from models.value_objects.link import Link
from models.value_objects.season_ref import SeasonRef


@dataclass
class EngineRestriction(ValidatedModel):
    year: list[SeasonRef | dict[str, Any]] = field(default_factory=list)
    size: dict[str, Any] | None = None
    type_of_engine: list[Link | dict[str, Any]] = field(default_factory=list)
    fuel_limit_per_race: dict[str, Any] | None = None
    fuel_flow_rate: dict[str, Any] | None = None
    fuel_injection_pressure_limit: dict[str, Any] | None = None
    engine_rpm_limit: dict[str, Any] | None = None
    power_output: dict[str, Any] | None = None

    def validate(self) -> None:
        self.year = list(core_normalize_season_items(self.year))
        self.type_of_engine = [
            Link.from_dict(item)
            for item in normalize_link_items(
                self.type_of_engine,
                field_name="type_of_engine",
            )
        ]
        self.size = normalize_unit_value(self.size, "size")
        self.fuel_limit_per_race = self._normalize_fuel_limit(self.fuel_limit_per_race)
        self.fuel_flow_rate = self._normalize_flow_rate(self.fuel_flow_rate)
        self.fuel_injection_pressure_limit = self._normalize_limit(
            self.fuel_injection_pressure_limit,
            "fuel_injection_pressure_limit",
        )
        self.engine_rpm_limit = self._normalize_limit(
            self.engine_rpm_limit,
            "engine_rpm_limit",
            range_key="limit",
        )
        self.power_output = normalize_range_value(self.power_output, "power_output")

    @staticmethod
    def _normalize_fuel_limit(value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            msg = "Pole fuel_limit_per_race musi być słownikiem"
            raise TypeError(msg)
        result: dict[str, Any] = dict(value)
        if "range_kg" in result:
            result["range_kg"] = normalize_range_value(
                result.get("range_kg"),
                "fuel_limit_per_race.range_kg",
            )
        if "range_l" in result:
            result["range_l"] = normalize_range_value(
                result.get("range_l"),
                "fuel_limit_per_race.range_l",
            )
        return result

    @staticmethod
    def _normalize_flow_rate(value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            msg = "Pole fuel_flow_rate musi być słownikiem"
            raise TypeError(msg)
        result: dict[str, Any] = dict(value)
        if "rate" in result:
            result["rate"] = normalize_unit_value(
                result.get("rate"),
                "fuel_flow_rate.rate",
            )
        if "applies_above_rpm" in result:
            result["applies_above_rpm"] = normalize_unit_value(
                result.get("applies_above_rpm"),
                "fuel_flow_rate.applies_above_rpm",
            )
        return result

    @staticmethod
    def _normalize_limit(
        value: dict[str, Any] | None,
        field_name: str,
        *,
        range_key: str | None = None,
    ) -> dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            msg = f"Pole {field_name} musi być słownikiem"
            raise TypeError(msg)
        result: dict[str, Any] = dict(value)
        key = range_key or "limit"
        if key in result:
            limit_value = result.get(key)
            if isinstance(limit_value, dict) and "min" in limit_value:
                result[key] = normalize_range_value(limit_value, f"{field_name}.{key}")
            else:
                result[key] = normalize_unit_value(limit_value, f"{field_name}.{key}")
        return result
