from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from scrapers.base.postprocess import BaseRecordAssembler
from scrapers.base.postprocess import BaseRecordAssemblerInput


@dataclass(frozen=True)
class SeasonRecordSections:
    entries: list[dict[str, Any]]
    free_practice_drivers: list[dict[str, Any]]
    calendar: list[dict[str, Any]]
    cancelled_rounds: list[dict[str, Any]]
    testing_venues_and_dates: list[dict[str, Any]]
    results: list[dict[str, Any]]
    non_championship_races: list[dict[str, Any]]
    scoring_system: list[dict[str, Any]]
    drivers_standings: list[dict[str, Any]]
    constructors_standings: list[dict[str, Any]]
    jim_clark_trophy: list[dict[str, Any]]
    colin_chapman_trophy: list[dict[str, Any]]
    south_african_formula_one_championship: list[dict[str, Any]]
    british_formula_one_championship: list[dict[str, Any]]
    regulation_changes: list[dict[str, Any]]
    mid_season_changes: list[dict[str, Any]]

    @classmethod
    def empty(cls) -> SeasonRecordSections:
        return cls(
            entries=[],
            free_practice_drivers=[],
            calendar=[],
            cancelled_rounds=[],
            testing_venues_and_dates=[],
            results=[],
            non_championship_races=[],
            scoring_system=[],
            drivers_standings=[],
            constructors_standings=[],
            jim_clark_trophy=[],
            colin_chapman_trophy=[],
            south_african_formula_one_championship=[],
            british_formula_one_championship=[],
            regulation_changes=[],
            mid_season_changes=[],
        )


@dataclass(frozen=True)
class SeasonPayloadDTO:
    sections: SeasonRecordSections
    base: BaseRecordAssemblerInput = BaseRecordAssemblerInput()


class SeasonRecordAssembler(BaseRecordAssembler):
    _SECTION_KEYS: tuple[str, ...] = (
        "entries",
        "free_practice_drivers",
        "calendar",
        "cancelled_rounds",
        "testing_venues_and_dates",
        "results",
        "non_championship_races",
        "scoring_system",
        "drivers_standings",
        "constructors_standings",
        "jim_clark_trophy",
        "colin_chapman_trophy",
        "south_african_formula_one_championship",
        "british_formula_one_championship",
        "regulation_changes",
        "mid_season_changes",
    )

    def assemble(
        self,
        payload: SeasonPayloadDTO | SeasonRecordSections,
    ) -> dict[str, Any]:
        dto = (
            payload
            if isinstance(payload, SeasonPayloadDTO)
            else SeasonPayloadDTO(sections=payload)
        )
        record = super().assemble(payload=dto.base)
        record.update(self._map_sections(dto.sections))
        return record

    def _map_sections(self, sections: SeasonRecordSections) -> dict[str, Any]:
        return {key: getattr(sections, key) for key in self._SECTION_KEYS}
