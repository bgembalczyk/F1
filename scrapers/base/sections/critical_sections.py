from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CriticalSection:
    section_id: str
    alternative_section_ids: tuple[str, ...] = ()


DOMAIN_CRITICAL_SECTIONS: dict[str, tuple[CriticalSection, ...]] = {
    "drivers": (
        CriticalSection(section_id="Career_results", alternative_section_ids=("Racing_record", "Karting_record")),
    ),
    "constructors": (
        CriticalSection(section_id="Constructors"),
    ),
    "circuits": (
        CriticalSection(section_id="Circuits"),
        CriticalSection(section_id="Lap_records", alternative_section_ids=("Formula_One_lap_records",)),
    ),
    "seasons": (
        CriticalSection(section_id="Calendar"),
        CriticalSection(
            section_id="World_Drivers'_Championship_standings",
            alternative_section_ids=("World_Championship_of_Drivers_standings",),
        ),
        CriticalSection(
            section_id="World_Constructors'_Championship_standings",
            alternative_section_ids=("International_Cup_for_F1_Constructors_standings",),
        ),
    ),
    "grands_prix": (
        CriticalSection(
            section_id="By_year",
            alternative_section_ids=(
                "Winners",
                "By_year:_the_European_Grand_Prix_as_a_standalone_event",
                "Winners_of_the_Caesars_Palace_Grand_Prix",
            ),
        ),
        CriticalSection(
            section_id="Red-flagged_races",
            alternative_section_ids=(
                "List_of_red-flagged_Formula_One_World_Championship_races",
                "Formula_One_World_Championship_red-flagged_races",
            ),
        ),
        CriticalSection(
            section_id="Non-championship_races",
            alternative_section_ids=(
                "List_of_red-flagged_non-championship_Formula_One_races",
            ),
        ),
    ),
}
