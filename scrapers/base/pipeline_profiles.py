from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any

from scrapers.base.helpers.common_config import ScraperCommonConfig
from scrapers.base.options import ScraperOptions


@dataclass(frozen=True)
class PipelineProfile:
    common_config: ScraperCommonConfig


@dataclass(frozen=True)
class ScraperPipelineBinding:
    validator_factory: str | None = None
    transformer_factories: tuple[str, ...] = ()
    post_processors: tuple[str, ...] = ()


PIPELINE_PROFILES: dict[str, PipelineProfile] = {
    "seed_soft": PipelineProfile(
        common_config=ScraperCommonConfig(
            include_urls=True,
            normalize_empty_values=True,
            validation_mode="soft",
        ),
    ),
    "seed_strict": PipelineProfile(
        common_config=ScraperCommonConfig(
            include_urls=True,
            normalize_empty_values=False,
            validation_mode="hard",
        ),
    ),
    "article_strict": PipelineProfile(
        common_config=ScraperCommonConfig(
            include_urls=True,
            normalize_empty_values=True,
            validation_mode="soft",
        ),
    ),
}

# Backward-compatible aliases.
PIPELINE_PROFILE_ALIASES: dict[str, str] = {
    "soft_seed": "seed_soft",
    "strict_seed": "seed_strict",
    "details": "article_strict",
}

DOMAIN_PROFILE_OVERRIDES: dict[str, dict[str, ScraperCommonConfig]] = {
    "circuits": {
        "seed_soft": ScraperCommonConfig(
            include_urls=True,
            normalize_empty_values=False,
            validation_mode="soft",
        ),
    },
}

SCRAPER_PIPELINE_BINDINGS: dict[str, ScraperPipelineBinding] = {
    "scrapers.circuits.list_scraper.CircuitsListScraper": ScraperPipelineBinding(
        validator_factory="scrapers.circuits.validator:CircuitsRecordValidator",
    ),
    "scrapers.drivers.list_scraper.F1DriversListScraper": ScraperPipelineBinding(
        validator_factory="scrapers.drivers.validator:DriversRecordValidator",
        transformer_factories=(
            "scrapers.base.transformers.drivers_championships:DriversChampionshipsTransformer",
        ),
    ),
    "scrapers.grands_prix.list_scraper.GrandsPrixListScraper": ScraperPipelineBinding(
        validator_factory="scrapers.grands_prix.validator:GrandsPrixRecordValidator",
    ),
    "scrapers.drivers.female_drivers_list.FemaleDriversListScraper": ScraperPipelineBinding(
        post_processors=(
            "scrapers.drivers.post_processors:EntriesStartsPointsPostProcessor",
        ),
    ),
    "scrapers.drivers.single_scraper.SingleDriverScraper": ScraperPipelineBinding(
        post_processors=(
            "scrapers.drivers.postprocess.contract:DriverSectionContractPostProcessor",
        ),
    ),
    "scrapers.constructors.single_scraper.SingleConstructorScraper": ScraperPipelineBinding(
        post_processors=(
            "scrapers.constructors.postprocess.contract:ConstructorSectionContractPostProcessor",
        ),
    ),
    "scrapers.circuits.single_scraper.F1SingleCircuitScraper": ScraperPipelineBinding(
        post_processors=(
            "scrapers.circuits.postprocess.contract:CircuitSectionContractPostProcessor",
        ),
    ),
    "scrapers.seasons.single_scraper.SingleSeasonScraper": ScraperPipelineBinding(
        post_processors=(
            "scrapers.seasons.postprocess.contract:SeasonSectionContractPostProcessor",
        ),
    ),
    "scrapers.grands_prix.single_scraper.F1SingleGrandPrixScraper": ScraperPipelineBinding(
        post_processors=(
            "scrapers.grands_prix.postprocess.contract:GrandPrixSectionContractPostProcessor",
        ),
    ),
    "scrapers.drivers.fatalities_list_scraper.F1FatalitiesListScraper": ScraperPipelineBinding(
        transformer_factories=(
            "scrapers.base.transformers.fatalities_car:FatalitiesCarTransformer",
        ),
    ),
    "scrapers.grands_prix.red_flagged_races_scraper.base.RedFlaggedRacesBaseScraper": ScraperPipelineBinding(
        transformer_factories=(
            "scrapers.base.transformers.failed_to_make_restart:FailedToMakeRestartTransformer",
        ),
    ),
    "scrapers.points.points_scoring_systems_history.PointsScoringSystemsHistoryScraper": ScraperPipelineBinding(
        transformer_factories=(
            "scrapers.base.transformers.points_scoring_systems_history:PointsScoringSystemsHistoryTransformer",
        ),
    ),
    "scrapers.points.shortened_race_points.ShortenedRacePointsScraper": ScraperPipelineBinding(
        transformer_factories=(
            "scrapers.base.transformers.shortened_race_points:ShortenedRacePointsTransformer",
        ),
    ),
}


def _normalized_profile_name(profile: str) -> str:
    normalized = profile.strip().lower()
    return PIPELINE_PROFILE_ALIASES.get(normalized, normalized)


def get_pipeline_profile(profile: str) -> PipelineProfile:
    profile_name = _normalized_profile_name(profile)
    resolved = PIPELINE_PROFILES.get(profile_name)
    if resolved is not None:
        return resolved
    msg = f"Unknown scraper config profile: {profile}"
    raise ValueError(msg)


def resolve_profile_config(*, domain: str | None, profile: str) -> ScraperCommonConfig:
    profile_name = _normalized_profile_name(profile)
    resolved_profile = get_pipeline_profile(profile_name)
    if not domain:
        return resolved_profile.common_config

    domain_overrides = DOMAIN_PROFILE_OVERRIDES.get(domain.strip().lower(), {})
    return domain_overrides.get(profile_name, resolved_profile.common_config)


def _resolve_object(factory_path: str) -> Any:
    module_name, object_name = factory_path.split(":", maxsplit=1)
    module = import_module(module_name)
    return getattr(module, object_name)


def _scraper_key(scraper_cls: type[Any]) -> str:
    return f"{scraper_cls.__module__}.{scraper_cls.__name__}"


def apply_scraper_pipeline_bindings(
    options: ScraperOptions,
    *,
    scraper_cls: type[Any],
) -> ScraperOptions:
    binding = SCRAPER_PIPELINE_BINDINGS.get(_scraper_key(scraper_cls))
    if binding is None:
        return options

    if options.validator is None and binding.validator_factory is not None:
        validator_cls = _resolve_object(binding.validator_factory)
        options.validator = validator_cls()

    for transformer_path in binding.transformer_factories:
        transformer_cls = _resolve_object(transformer_path)
        if any(
            isinstance(transformer, transformer_cls)
            for transformer in options.transformers
        ):
            continue
        options.transformers.append(transformer_cls())

    for post_processor_path in binding.post_processors:
        post_processor_cls = _resolve_object(post_processor_path)
        if any(
            isinstance(post_processor, post_processor_cls)
            for post_processor in options.post_processors
        ):
            continue
        options.post_processors.append(post_processor_cls())

    return options
