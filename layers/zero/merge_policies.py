from __future__ import annotations

import re
from collections.abc import Callable  # noqa: TC003
from typing import Protocol

from scrapers.wiki.constants import DRIVER_FATALITIES_SOURCE
from scrapers.wiki.constants import F1_CONSTRUCTORS_BY_YEAR_PATTERN
from scrapers.wiki.constants import F1_DRIVERS_SOURCE
from scrapers.wiki.constants import FEMALE_DRIVERS_SOURCE
from scrapers.wiki.constants import PRIVATEER_TEAMS_SOURCE
from scrapers.wiki.constants import SPONSORSHIP_LIVERIES_SOURCE


class MergePolicy(Protocol):
    def supports(self, source_name: str) -> bool: ...

    def apply(self, record: dict[str, object]) -> dict[str, object]: ...


class DriversMergePolicy:
    def __init__(
        self,
        *,
        transform_f1_driver: Callable[[dict[str, object]], dict[str, object]],
        transform_female_driver: Callable[[dict[str, object]], dict[str, object]],
        attach_driver_death_data: Callable[[dict[str, object]], None],
    ) -> None:
        self._transform_f1_driver = transform_f1_driver
        self._transform_female_driver = transform_female_driver
        self._attach_driver_death_data = attach_driver_death_data
        self._matched_source_name: str | None = None

    def supports(self, source_name: str) -> bool:
        supported = source_name in {
            F1_DRIVERS_SOURCE,
            FEMALE_DRIVERS_SOURCE,
            DRIVER_FATALITIES_SOURCE,
        }
        self._matched_source_name = source_name if supported else None
        return supported

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        if self._matched_source_name == F1_DRIVERS_SOURCE:
            return self._transform_f1_driver(record)
        if self._matched_source_name == FEMALE_DRIVERS_SOURCE:
            return self._transform_female_driver(record)
        if self._matched_source_name == DRIVER_FATALITIES_SOURCE:
            self._attach_driver_death_data(record)
        return record


class TeamsMergePolicy:
    def __init__(
        self,
        *,
        build_racing_series: Callable[[dict[str, object]], dict[str, object]],
    ) -> None:
        self._build_racing_series = build_racing_series
        self._matched_source_name: str | None = None

    def supports(self, source_name: str) -> bool:
        supported = bool(
            re.fullmatch(F1_CONSTRUCTORS_BY_YEAR_PATTERN, source_name),
        ) or (source_name in {SPONSORSHIP_LIVERIES_SOURCE, PRIVATEER_TEAMS_SOURCE})
        self._matched_source_name = source_name if supported else None
        return supported

    def apply(self, record: dict[str, object]) -> dict[str, object]:
        transformed = dict(record)
        source_name = self._matched_source_name or ""
        if re.fullmatch(F1_CONSTRUCTORS_BY_YEAR_PATTERN, source_name):
            transformed = {
                "team": transformed.get("constructor"),
                "racing_series": self._build_racing_series({**transformed}),
            }
        if source_name == SPONSORSHIP_LIVERIES_SOURCE and "liveries" in transformed:
            transformed["racing_series"] = self._build_racing_series(
                {"liveries": transformed.pop("liveries")},
            )
        if source_name == PRIVATEER_TEAMS_SOURCE:
            formula_one = {
                key: transformed.pop(key) for key in ("seasons",) if key in transformed
            }
            formula_one["privateer"] = True
            transformed["racing_series"] = self._build_racing_series(formula_one)
        return transformed
