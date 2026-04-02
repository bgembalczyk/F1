from __future__ import annotations

import logging
import warnings
from dataclasses import dataclass

from scrapers.base.run_profiles import LegacyCliProfileName


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WikiSourceDefinition:
    domain: str
    seed_name: str
    source_name: str
    output_file: str
    profile: LegacyCliProfileName = "list_scraper"

    @property
    def output_category(self) -> str:
        """Backward-compatible alias for legacy naming used by older call-sites."""
        return self.domain

    @property
    def list_filename(self) -> str:
        """Backward-compatible alias for legacy naming used by older call-sites."""
        return self.output_file


WIKI_SOURCE_DEFINITIONS: tuple[WikiSourceDefinition, ...] = (
    WikiSourceDefinition("circuits", "circuits", "circuits", "f1_circuits.json"),
    WikiSourceDefinition(
        "constructors",
        "constructors_current",
        "constructors_current",
        "f1_constructors_{year}.json",
    ),
    WikiSourceDefinition(
        "chassis_constructors",
        "constructors_former",
        "constructors_former",
        "f1_former_constructors.json",
    ),
    WikiSourceDefinition(
        "chassis_constructors",
        "constructors_indianapolis_only",
        "constructors_indianapolis_only",
        "f1_indianapolis_only_constructors.json",
    ),
    WikiSourceDefinition("teams", "constructors_privateer", "constructors_privateer", "f1_privateer_teams.json"),
    WikiSourceDefinition("drivers", "drivers", "drivers", "f1_drivers.json"),
    WikiSourceDefinition("drivers", "drivers_female", "drivers_female", "female_drivers.json"),
    WikiSourceDefinition("drivers", "drivers_fatalities", "drivers_fatalities", "f1_driver_fatalities.json"),
    WikiSourceDefinition("seasons", "seasons", "seasons", "f1_seasons.json"),
    WikiSourceDefinition(
        "grands_prix",
        "grands_prix_by_title",
        "grands_prix_by_title",
        "f1_grands_prix_by_title.json",
    ),
    WikiSourceDefinition(
        "engines",
        "engines_indianapolis_only",
        "engines_indianapolis_only",
        "f1_indianapolis_only_engine_manufacturers.json",
    ),
    WikiSourceDefinition("rules", "engines_restrictions", "engines_restrictions", "f1_engine_restrictions.json"),
    WikiSourceDefinition("rules", "engines_regulations", "engines_regulations", "f1_engine_regulations.json"),
    WikiSourceDefinition("engines", "engines_manufacturers", "engines_manufacturers", "f1_engine_manufacturers.json"),
    WikiSourceDefinition(
        "races",
        "grands_prix_red_flagged_world_championship",
        "grands_prix_red_flagged_world_championship",
        "f1_red_flagged_world_championship_races.json",
    ),
    WikiSourceDefinition(
        "races",
        "grands_prix_red_flagged_non_championship",
        "grands_prix_red_flagged_non_championship",
        "f1_red_flagged_non_championship_races.json",
    ),
    WikiSourceDefinition("points", "points_sprint", "points_sprint", "points_scoring_systems_sprint.json"),
    WikiSourceDefinition(
        "points",
        "points_shortened",
        "points_shortened",
        "points_scoring_systems_shortened.json",
    ),
    WikiSourceDefinition("points", "points_history", "points_history", "points_scoring_systems_history.json"),
    WikiSourceDefinition("seasons", "tyres", "tyres", "f1_tyre_manufacturers_by_season.json"),
    WikiSourceDefinition("teams", "sponsorship_liveries", "sponsorship_liveries", "f1_sponsorship_liveries.json"),
)

SOURCE_BY_SEED_NAME: dict[str, WikiSourceDefinition] = {
    source.seed_name: source for source in WIKI_SOURCE_DEFINITIONS
}
SOURCE_BY_SOURCE_NAME: dict[str, WikiSourceDefinition] = {
    source.source_name: source for source in WIKI_SOURCE_DEFINITIONS
}
SOURCE_BY_LIST_FILENAME: dict[str, WikiSourceDefinition] = {
    source.output_file: source for source in WIKI_SOURCE_DEFINITIONS
}

LEGACY_SEED_NAME_ALIASES: dict[str, str] = {
    "constructors": "constructors_current",
    "grands_prix": "grands_prix_by_title",
}

LEGACY_LIST_FILENAME_ALIASES: dict[str, str] = {
    "f1_engine_manufacturers_indianapolis_only.json": "f1_indianapolis_only_engine_manufacturers.json",
}
ENGINES_INDIANAPOLIS_ONLY_LEGACY_SOURCE = (
    "f1_engine_manufacturers_indianapolis_only.json"
)

FORMER_CONSTRUCTORS_SOURCE = SOURCE_BY_SEED_NAME["constructors_former"].list_filename
INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE = SOURCE_BY_SEED_NAME[
    "constructors_indianapolis_only"
].list_filename
TYRE_MANUFACTURERS_SOURCE = SOURCE_BY_SEED_NAME["tyres"].list_filename
INDIANAPOLIS_ONLY_ENGINES_SOURCE = SOURCE_BY_SEED_NAME[
    "engines_indianapolis_only"
].output_file


def _emit_deprecation_warning(kind: str, legacy: str, canonical: str) -> None:
    message = (
        f"Legacy {kind} alias '{legacy}' is deprecated and will be removed in a future release; "
        f"use canonical value '{canonical}'."
    )
    logger.warning(message)
    warnings.warn(
        message,
        DeprecationWarning,
        stacklevel=3,
    )


def resolve_seed_name(seed_name: str, *, warn: bool = True) -> str:
    canonical = LEGACY_SEED_NAME_ALIASES.get(seed_name, seed_name)
    if canonical != seed_name and warn:
        _emit_deprecation_warning("seed_name", seed_name, canonical)
    return canonical


def resolve_list_filename(list_filename: str, *, warn: bool = True) -> str:
    canonical = LEGACY_LIST_FILENAME_ALIASES.get(list_filename, list_filename)
    if canonical != list_filename and warn:
        _emit_deprecation_warning("list filename", list_filename, canonical)
    return canonical


def get_source_by_seed_name(seed_name: str, *, warn: bool = True) -> WikiSourceDefinition:
    canonical_seed_name = resolve_seed_name(seed_name, warn=warn)
    try:
        return SOURCE_BY_SEED_NAME[canonical_seed_name]
    except KeyError as exc:
        msg = f"Unknown wiki source seed_name: {seed_name!r}"
        raise KeyError(msg) from exc


def get_source_by_list_filename(
    list_filename: str,
    *,
    warn: bool = True,
) -> WikiSourceDefinition:
    canonical_list_filename = resolve_list_filename(list_filename, warn=warn)
    try:
        return SOURCE_BY_LIST_FILENAME[canonical_list_filename]
    except KeyError as exc:
        msg = f"Unknown wiki source list filename: {list_filename!r}"
        raise KeyError(msg) from exc


def get_source_by_source_name(source_name: str) -> WikiSourceDefinition:
    try:
        return SOURCE_BY_SOURCE_NAME[source_name]
    except KeyError as exc:
        msg = f"Unknown wiki source source_name: {source_name!r}"
        raise KeyError(msg) from exc


def validate_sources_registry_consistency() -> None:
    seen_seed_names: set[str] = set()
    seen_source_names: set[str] = set()
    seen_filenames: set[str] = set()

    for source in WIKI_SOURCE_DEFINITIONS:
        if source.domain.strip() == "":
            msg = f"Empty domain in wiki sources registry for seed: {source.seed_name}"
            raise ValueError(msg)
        if source.seed_name in seen_seed_names:
            msg = f"Duplicate canonical seed_name in wiki sources registry: {source.seed_name}"
            raise ValueError(msg)
        seen_seed_names.add(source.seed_name)

        if source.source_name in seen_source_names:
            msg = f"Duplicate canonical source_name in wiki sources registry: {source.source_name}"
            raise ValueError(msg)
        seen_source_names.add(source.source_name)

        if source.output_file in seen_filenames:
            msg = (
                "Duplicate canonical list_filename in wiki sources registry: "
                f"{source.output_file}"
            )
            raise ValueError(msg)
        seen_filenames.add(source.output_file)

        if source.seed_name != source.source_name and source.source_name in seen_seed_names:
            msg = (
                "Source registry naming conflict: source_name duplicates an existing seed_name: "
                f"{source.source_name!r}"
            )
            raise ValueError(msg)

    for legacy_seed_name, canonical_seed_name in LEGACY_SEED_NAME_ALIASES.items():
        if legacy_seed_name in SOURCE_BY_SEED_NAME:
            msg = (
                "Legacy seed alias conflicts with canonical seed_name: "
                f"{legacy_seed_name}"
            )
            raise ValueError(msg)
        if canonical_seed_name not in SOURCE_BY_SEED_NAME:
            msg = (
                "Legacy seed alias points to missing canonical seed: "
                f"{legacy_seed_name} -> {canonical_seed_name}"
            )
            raise ValueError(msg)

    for legacy_filename, canonical_filename in LEGACY_LIST_FILENAME_ALIASES.items():
        if legacy_filename in SOURCE_BY_LIST_FILENAME:
            msg = (
                "Legacy list filename alias conflicts with canonical list filename: "
                f"{legacy_filename}"
            )
            raise ValueError(msg)
        if canonical_filename not in SOURCE_BY_LIST_FILENAME:
            msg = (
                "Legacy filename alias points to missing canonical list filename: "
                f"{legacy_filename} -> {canonical_filename}"
            )
            raise ValueError(msg)


validate_sources_registry_consistency()


__all__ = [
    "FORMER_CONSTRUCTORS_SOURCE",
    "ENGINES_INDIANAPOLIS_ONLY_LEGACY_SOURCE",
    "INDIANAPOLIS_ONLY_ENGINES_SOURCE",
    "INDIANAPOLIS_ONLY_CONSTRUCTORS_SOURCE",
    "LEGACY_LIST_FILENAME_ALIASES",
    "LEGACY_SEED_NAME_ALIASES",
    "SOURCE_BY_LIST_FILENAME",
    "SOURCE_BY_SOURCE_NAME",
    "SOURCE_BY_SEED_NAME",
    "TYRE_MANUFACTURERS_SOURCE",
    "WIKI_SOURCE_DEFINITIONS",
    "WikiSourceDefinition",
    "get_source_by_list_filename",
    "get_source_by_source_name",
    "get_source_by_seed_name",
    "resolve_list_filename",
    "resolve_seed_name",
    "validate_sources_registry_consistency",
]
