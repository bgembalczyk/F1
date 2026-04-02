from __future__ import annotations

from .base import DomainTransformStrategy
from .shared import build_racing_series
from .shared import normalize_driver_series_stats


class DriversDomainTransformStrategy(DomainTransformStrategy):
    def transform(self, record: dict[str, object], source_name: str) -> dict[str, object]:
        transformed = dict(record)
        if source_name == "f1_drivers.json":
            return self._transform_f1_driver(transformed)
        if source_name == "female_drivers.json":
            return self._transform_female_driver(transformed)
        if source_name == "f1_driver_fatalities.json":
            self._attach_driver_death_data(transformed)
        return transformed

    def _transform_f1_driver(self, transformed: dict[str, object]) -> dict[str, object]:
        driver = transformed.pop("driver", None)
        nationality = transformed.pop("nationality", None)
        formula_one = normalize_driver_series_stats(transformed)
        return {
            "driver": driver,
            "nationality": nationality,
            "racing_series": build_racing_series(formula_one),
        }

    def _transform_female_driver(self, transformed: dict[str, object]) -> dict[str, object]:
        driver = transformed.pop("driver", None)
        formula_one = normalize_driver_series_stats(transformed)
        return {
            "driver": driver,
            "gender": "female",
            "racing_series": build_racing_series(formula_one),
        }

    def _attach_driver_death_data(self, transformed: dict[str, object]) -> None:
        death_fields = {key: transformed.pop(key) for key in ("date", "age") if key in transformed}
        crash_fields = {
            key: transformed.pop(key)
            for key in ("event", "circuit", "car", "session")
            if key in transformed
        }
        transformed["death"] = {**death_fields, "crash": crash_fields}
