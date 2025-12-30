from dataclasses import dataclass, field
from typing import Any, Dict, List

from models.validation.base import ValidatedModel
from models.validation.helpers import normalize_text
from models.validation.helpers import normalize_unit_list
from models.validation.helpers import normalize_unit_value
from models.validation.validators import normalize_season_list, validate_float
from models.value_objects.season_ref import SeasonRef


@dataclass
class EngineRegulation(ValidatedModel):
    seasons: List[SeasonRef | dict[str, Any]] = field(default_factory=list)
    operating_principle: str | None = None
    maximum_displacement: Dict[str, Any] | None = None
    configuration: Dict[str, Any] | None = None
    rpm_limit: Dict[str, Any] | None = None
    fuel_flow_limit: str | None = None
    fuel_composition: Dict[str, Any] | None = None

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        self.seasons = normalize_season_list(self.seasons)
        self.operating_principle = normalize_text(self.operating_principle)
        self.maximum_displacement = self._normalize_displacement(
            self.maximum_displacement
        )
        self.configuration = self._normalize_configuration(self.configuration)
        self.rpm_limit = normalize_unit_value(self.rpm_limit, "rpm_limit")
        self.fuel_flow_limit = normalize_text(self.fuel_flow_limit)
        self.fuel_composition = self._normalize_fuel_composition(self.fuel_composition)

    def _normalize_displacement(
        self, value: Dict[str, Any] | None
    ) -> Dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("Pole maximum_displacement musi być słownikiem")
        result: Dict[str, Any] = dict(value)
        if "naturally_aspirated" in result:
            result["naturally_aspirated"] = normalize_unit_list(
                result.get("naturally_aspirated"),
                "maximum_displacement.naturally_aspirated",
            )
        if "forced_induction" in result:
            result["forced_induction"] = normalize_unit_list(
                result.get("forced_induction"),
                "maximum_displacement.forced_induction",
            )
        return result

    def _normalize_configuration(
        self, value: Dict[str, Any] | None
    ) -> Dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("Pole configuration musi być słownikiem")
        result: Dict[str, Any] = dict(value)
        result["text"] = normalize_text(result.get("text"))
        if "angle" in result:
            result["angle"] = normalize_unit_value(
                result.get("angle"), "configuration.angle"
            )
        if "type" in result:
            result["type"] = normalize_text(result.get("type"))
        extras = result.get("extras")
        if extras is None:
            result["extras"] = []
        elif not isinstance(extras, list):
            raise ValueError("Pole configuration.extras musi być listą")
        else:
            result["extras"] = [
                item.strip()
                for item in extras
                if isinstance(item, str) and item.strip()
            ]
        return result

    def _normalize_fuel_composition(
        self, value: Dict[str, Any] | None
    ) -> Dict[str, Any] | None:
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError("Pole fuel_composition musi być słownikiem")
        result: Dict[str, Any] = dict(value)
        if "alcohol" in result:
            result["alcohol"] = normalize_text(result.get("alcohol"))
        if "petrol" in result:
            result["petrol"] = normalize_text(result.get("petrol"))
        return result
