from dataclasses import dataclass, field
from typing import Any, Dict, List

from models.validation.base import ValidatedModel
from models.validation.validators import normalize_season_list, validate_float
from models.value_objects.season_ref import SeasonRef


def _normalize_unit_value(value: Any, field_name: str) -> Dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, dict):
        raw_value = value.get("value")
        unit = value.get("unit")
        normalized_value = (
            validate_float(raw_value, f"{field_name}.value")
            if raw_value is not None
            else None
        )
        normalized_unit = str(unit).strip() if unit is not None else None
        return {"value": normalized_value, "unit": normalized_unit}
    if isinstance(value, (int, float)):
        return {"value": validate_float(value, f"{field_name}.value"), "unit": None}
    raise ValueError(f"Pole {field_name} musi być słownikiem lub liczbą")


def _normalize_unit_list(value: Any, field_name: str) -> List[Dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"Pole {field_name} musi być listą")
    normalized: List[Dict[str, Any]] = []
    for index, item in enumerate(value):
        normalized_item = _normalize_unit_value(item, f"{field_name}[{index}]")
        if normalized_item is not None:
            normalized.append(normalized_item)
    return normalized


def _normalize_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


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
        self.operating_principle = _normalize_text(self.operating_principle)
        self.maximum_displacement = self._normalize_displacement(
            self.maximum_displacement
        )
        self.configuration = self._normalize_configuration(self.configuration)
        self.rpm_limit = _normalize_unit_value(self.rpm_limit, "rpm_limit")
        self.fuel_flow_limit = _normalize_text(self.fuel_flow_limit)
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
            result["naturally_aspirated"] = _normalize_unit_list(
                result.get("naturally_aspirated"),
                "maximum_displacement.naturally_aspirated",
            )
        if "forced_induction" in result:
            result["forced_induction"] = _normalize_unit_list(
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
        result["text"] = _normalize_text(result.get("text"))
        if "angle" in result:
            result["angle"] = _normalize_unit_value(
                result.get("angle"), "configuration.angle"
            )
        if "type" in result:
            result["type"] = _normalize_text(result.get("type"))
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
            result["alcohol"] = _normalize_text(result.get("alcohol"))
        if "petrol" in result:
            result["petrol"] = _normalize_text(result.get("petrol"))
        return result
