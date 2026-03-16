from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CriticalSection:
    section_id: str
    alternative_section_ids: tuple[str, ...] = ()


def section_id_to_label(section_id: str) -> str:
    return " ".join(
        section_id.replace("_", " ").replace("-", " ").replace("/", " / ").split(),
    )


def resolve_section_candidates(
    *,
    domain: str,
    section_id: str,
    alternative_section_ids: tuple[str, ...] = (),
) -> tuple[str, ...]:
    """Resolve section candidates in deterministic order.

    Order:
    1) canonical section ID,
    2) alternative IDs,
    3) text label fallback derived from canonical ID.
    """
    resolved_alternatives = alternative_section_ids
    if not resolved_alternatives:
        for candidate in DOMAIN_CRITICAL_SECTIONS.get(domain, ()):  # pragma: no branch
            if candidate.section_id == section_id:
                resolved_alternatives = candidate.alternative_section_ids
                break

    candidates: list[str] = [section_id]
    for alias in resolved_alternatives:
        if alias and alias not in candidates:
            candidates.append(alias)

    section_label = section_id_to_label(section_id)
    if section_label and section_label not in candidates:
        candidates.append(section_label)
    return tuple(candidates)


DOMAIN_CRITICAL_SECTIONS: dict[str, tuple[CriticalSection, ...]] = {
    "drivers": (
        CriticalSection(
            section_id="Career_results",
            alternative_section_ids=(
                "Career-results",
                "Career/results",
                "Racing_record",
                "Karting_record",
                "Motorsport_career_results",
                "Career_record",
                "Racing_career",
                "Formula_One_career",
                "F1_career_results",
                "Formula_One/World_Championship_results",
                "Formula_One_World_Championship_results",
                "Formula-One_World_Championship_results",
            ),
        ),
        CriticalSection(
            section_id="Non-championship",
            alternative_section_ids=(
                "Non_championship",
                "Non/championship",
                "Non-championship_races",
                "Non_championship_races",
                "Non_Championship",
                "Formula_One_non-championship_results",
            ),
        ),
    ),
    "constructors": (
        CriticalSection(
            section_id="Constructors",
            alternative_section_ids=(
                "Constructors_for_2024",
                "Constructors-for-the-current-season",
                "Teams",
                "Constructors'_Championship",
                "Current_constructors",
                "Current_teams",
                "Constructors_for_the_current_season",
            ),
        ),
        CriticalSection(
            section_id="Championship_results",
            alternative_section_ids=(
                "Championship-results",
                "Championship/results",
                "Formula_One/World_Championship_results",
                "Formula_One_World_Championship_results",
                "Formula-One_World_Championship_results",
                "World_Championship_results",
            ),
        ),
        CriticalSection(
            section_id="Complete_Formula_One_results",
            alternative_section_ids=(
                "Complete_Formula-One_results",
                "Complete_Formula_One/results",
                "Complete_World_Championship_results",
                "Complete_Formula_One/World_Championship_results",
                "Complete_Formula_One_World_Championship_results",
                "Complete_Formula-One_results",
            ),
        ),
        CriticalSection(
            section_id="History",
            alternative_section_ids=(
                "Team-History",
                "Team/History",
                "Team_history",
                "Racing_history",
                "Background",
            ),
        ),
    ),
    "circuits": (
        CriticalSection(
            section_id="Circuits",
            alternative_section_ids=(
                "F1_circuits",
                "Formula-One_circuits",
                "Current_circuits",
                "Active_circuits",
                "Formula_One_circuits",
                "List_of_Formula_One_circuits",
                "Current_Formula_One_circuits",
            ),
        ),
        CriticalSection(
            section_id="Layout_history",
            alternative_section_ids=(
                "Layout-history",
                "Layout/history",
                "History",
                "Circuit_layouts",
                "Track_layout",
                "Layout",
            ),
        ),
        CriticalSection(
            section_id="Lap_records",
            alternative_section_ids=(
                "Lap-records",
                "Lap/records",
                "Formula_One_lap_records",
                "Lap_record",
                "Official_lap_records",
                "Formula-One_lap_records",
            ),
        ),
        CriticalSection(
            section_id="Events",
            alternative_section_ids=(
                "Race_events",
                "Events/races",
                "Races",
                "Major_events",
                "Formula_One_Grands_Prix",
                "Formula_One/Grands_Prix",
            ),
        ),
    ),
    "seasons": (
        CriticalSection(
            section_id="Calendar",
            alternative_section_ids=(
                "Race-calendar",
                "Calendar/season",
                "Season_calendar",
                "Race_calendar",
                "Grands_Prix",
                "Championship_calendar",
                "World_Championship_calendar",
            ),
        ),
        CriticalSection(
            section_id="World_Drivers'_Championship_standings",
            alternative_section_ids=(
                "WDC_standings",
                "World-Drivers-Championship-standings",
                "World_Championship_of_Drivers_standings",
                "Drivers'_Championship_standings",
                "Drivers_standings",
                "World_Drivers_Championship_standings",
            ),
        ),
        CriticalSection(
            section_id="World_Constructors'_Championship_standings",
            alternative_section_ids=(
                "WCC_standings",
                "World-Constructors-Championship-standings",
                "International_Cup_for_F1_Constructors_standings",
                "Constructors'_Championship_standings",
                "Constructors_standings",
                "World_Constructors_Championship_standings",
            ),
        ),
        CriticalSection(
            section_id="Non-championship",
            alternative_section_ids=(
                "Non_championship",
                "Non/championship",
                "Non-championship_races",
                "Non_championship_races",
                "Non-championship_events",
                "Non_Championship",
            ),
        ),
    ),
    "grands_prix": (
        CriticalSection(
            section_id="By_year",
            alternative_section_ids=(
                "By-year",
                "By/year",
                "Winners",
                "Results_by_year",
                "By_season",
                "By_Year",
                "By_year:_the_European_Grand_Prix_as_a_standalone_event",
                "By_year_–_the_European_Grand_Prix_as_a_standalone_event",
                "Winners_of_the_Caesars_Palace_Grand_Prix",
            ),
        ),
        CriticalSection(
            section_id="Red-flagged_races",
            alternative_section_ids=(
                "Red_flagged-races",
                "Red-flagged/races",
                "List_of_red-flagged_Formula_One_World_Championship_races",
                "Formula_One_World_Championship_red-flagged_races",
                "Formula_One/World_Championship_red-flagged_races",
                "List_of_red_flagged_Formula_One_World_Championship_races",
                "Red_flagged_races",
            ),
        ),
        CriticalSection(
            section_id="Non-championship_races",
            alternative_section_ids=(
                "Non_championship-races",
                "Non-championship/races",
                "List_of_red-flagged_non-championship_Formula_One_races",
                "List_of_red_flagged_non-championship_Formula_One_races",
                "Red-flagged_non-championship_races",
                "Non-championship_red-flagged_races",
            ),
        ),
    ),
}
