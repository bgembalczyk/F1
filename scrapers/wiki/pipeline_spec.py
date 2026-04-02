from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WikiSourceSpec:
    seed_name: str
    list_filename: str


@dataclass(frozen=True)
class WikiDomainPipelineSpec:
    domain: str
    sources: tuple[WikiSourceSpec, ...]
    transformers: tuple[str, ...] = ()
    source_transformers: dict[str, tuple[str, ...]] | None = None
    postprocess: tuple[str, ...] = ()
    output_filename: str | None = None
    merge_enabled: bool = True


WIKI_PIPELINE_SPEC: tuple[WikiDomainPipelineSpec, ...] = (
    WikiDomainPipelineSpec(
        domain="circuits",
        sources=(WikiSourceSpec("circuits", "f1_circuits.json"),),
        transformers=("circuits_domain",),
    ),
    WikiDomainPipelineSpec(
        domain="constructors",
        sources=(
            WikiSourceSpec("constructors_current", "f1_constructors_{year}.json"),
        ),
        transformers=("constructor_domain",),
        postprocess=("sort_constructors_by_name",),
    ),
    WikiDomainPipelineSpec(
        domain="chassis_constructors",
        sources=(
            WikiSourceSpec("constructors_former", "f1_former_constructors.json"),
            WikiSourceSpec(
                "constructors_indianapolis_only",
                "f1_indianapolis_only_constructors.json",
            ),
        ),
        transformers=("constructor_domain",),
        postprocess=("sort_constructors_by_name",),
    ),
    WikiDomainPipelineSpec(
        domain="teams",
        sources=(
            WikiSourceSpec("constructors_privateer", "f1_privateer_teams.json"),
            WikiSourceSpec("sponsorship_liveries", "f1_sponsorship_liveries.json"),
        ),
        transformers=("teams_domain",),
        postprocess=(
            "merge_duplicate_teams",
            "nest_team_liveries",
            "sort_teams_by_name",
        ),
    ),
    WikiDomainPipelineSpec(
        domain="drivers",
        sources=(
            WikiSourceSpec("drivers", "f1_drivers.json"),
            WikiSourceSpec("drivers_female", "female_drivers.json"),
            WikiSourceSpec("drivers_fatalities", "f1_driver_fatalities.json"),
        ),
        transformers=("drivers_domain",),
        postprocess=("merge_duplicate_drivers", "sort_drivers_by_name"),
    ),
    WikiDomainPipelineSpec(
        domain="seasons",
        sources=(
            WikiSourceSpec("seasons", "f1_seasons.json"),
            WikiSourceSpec("tyres", "f1_tyre_manufacturers_by_season.json"),
        ),
        postprocess=("sort_seasons_by_year",),
    ),
    WikiDomainPipelineSpec(
        domain="grands_prix",
        sources=(WikiSourceSpec("grands_prix_by_title", "f1_grands_prix_by_title.json"),),
        transformers=("grands_prix_domain",),
    ),
    WikiDomainPipelineSpec(
        domain="races",
        sources=(
            WikiSourceSpec(
                "grands_prix_red_flagged_world_championship",
                "f1_red_flagged_world_championship_races.json",
            ),
            WikiSourceSpec(
                "grands_prix_red_flagged_non_championship",
                "f1_red_flagged_non_championship_races.json",
            ),
        ),
        transformers=("races_domain",),
    ),
    WikiDomainPipelineSpec(
        domain="engines",
        sources=(
            WikiSourceSpec(
                "engines_indianapolis_only",
                "f1_indianapolis_only_engine_manufacturers.json",
            ),
            WikiSourceSpec("engines_manufacturers", "f1_engine_manufacturers.json"),
        ),
        transformers=("engines_domain",),
    ),
    WikiDomainPipelineSpec(
        domain="rules",
        sources=(
            WikiSourceSpec("engines_restrictions", "f1_engine_restrictions.json"),
            WikiSourceSpec("engines_regulations", "f1_engine_regulations.json"),
        ),
        merge_enabled=False,
    ),
    WikiDomainPipelineSpec(
        domain="points",
        sources=(
            WikiSourceSpec("points_sprint", "points_scoring_systems_sprint.json"),
            WikiSourceSpec("points_shortened", "points_scoring_systems_shortened.json"),
            WikiSourceSpec("points_history", "points_scoring_systems_history.json"),
        ),
        merge_enabled=False,
    ),
)

LEGACY_SEED_NAME_ALIASES: dict[str, str] = {
    "constructors": "constructors_current",
    "grands_prix": "grands_prix_by_title",
}

LEGACY_LIST_FILENAME_ALIASES: dict[str, str] = {
    "f1_engine_manufacturers_indianapolis_only.json": "f1_indianapolis_only_engine_manufacturers.json",
}


def iter_source_specs() -> tuple[tuple[str, str, str], ...]:
    specs: list[tuple[str, str, str]] = []
    for domain_spec in WIKI_PIPELINE_SPEC:
        for source in domain_spec.sources:
            specs.append((source.seed_name, domain_spec.domain, source.list_filename))
    return tuple(specs)


def get_pipeline_spec_for_domain(domain: str) -> WikiDomainPipelineSpec | None:
    for spec in WIKI_PIPELINE_SPEC:
        if spec.domain == domain:
            return spec
    return None


def validate_wiki_pipeline_spec() -> None:
    seen_domains: set[str] = set()
    seen_seed_names: set[str] = set()
    seen_filenames: set[str] = set()

    for domain_spec in WIKI_PIPELINE_SPEC:
        if domain_spec.domain in seen_domains:
            msg = f"Duplicate domain in wiki pipeline spec: {domain_spec.domain!r}"
            raise ValueError(msg)
        seen_domains.add(domain_spec.domain)

        if not domain_spec.sources:
            msg = f"Domain {domain_spec.domain!r} has no sources in wiki pipeline spec"
            raise ValueError(msg)

        for source in domain_spec.sources:
            if source.seed_name in seen_seed_names:
                msg = f"Duplicate seed_name in wiki pipeline spec: {source.seed_name!r}"
                raise ValueError(msg)
            seen_seed_names.add(source.seed_name)

            if source.list_filename in seen_filenames:
                msg = f"Duplicate list_filename in wiki pipeline spec: {source.list_filename!r}"
                raise ValueError(msg)
            seen_filenames.add(source.list_filename)

        source_transformers = domain_spec.source_transformers or {}
        for filename in source_transformers:
            if filename not in {source.list_filename for source in domain_spec.sources}:
                msg = (
                    f"Domain {domain_spec.domain!r} defines source transformer for unknown "
                    f"filename {filename!r}"
                )
                raise ValueError(msg)

    for legacy_seed_name, canonical_seed_name in LEGACY_SEED_NAME_ALIASES.items():
        if canonical_seed_name not in seen_seed_names:
            msg = (
                "Legacy seed alias points to missing canonical seed: "
                f"{legacy_seed_name} -> {canonical_seed_name}"
            )
            raise ValueError(msg)

    for legacy_filename, canonical_filename in LEGACY_LIST_FILENAME_ALIASES.items():
        if canonical_filename not in seen_filenames:
            msg = (
                "Legacy filename alias points to missing canonical list filename: "
                f"{legacy_filename} -> {canonical_filename}"
            )
            raise ValueError(msg)


validate_wiki_pipeline_spec()


__all__ = [
    "LEGACY_LIST_FILENAME_ALIASES",
    "LEGACY_SEED_NAME_ALIASES",
    "WIKI_PIPELINE_SPEC",
    "WikiDomainPipelineSpec",
    "WikiSourceSpec",
    "get_pipeline_spec_for_domain",
    "iter_source_specs",
    "validate_wiki_pipeline_spec",
]
