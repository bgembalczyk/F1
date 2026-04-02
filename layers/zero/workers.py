from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.path_resolver import format_domain_year_name
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.zero.run_profile_paths import layer_zero_raw_paths
from scrapers.base.run_config import RunConfig
from scrapers.base.runner import ScraperRunner


@dataclass(frozen=True)
class LayerZeroConfigFactoryResolutionInput:
    config_factories_builder: Callable[[], dict[str, LayerZeroRunConfigFactoryProtocol]]


class LayerZeroConfigFactoryResolver:
    def resolve(
        self,
        data: LayerZeroConfigFactoryResolutionInput,
    ) -> dict[str, LayerZeroRunConfigFactoryProtocol]:
        return data.config_factories_builder()


@dataclass(frozen=True)
class LayerZeroLocalRunConfigInput:
    run_config: RunConfig
    job: ListJobRegistryEntry
    config_factories: dict[str, LayerZeroRunConfigFactoryProtocol]
    default_config_factory: LayerZeroRunConfigFactoryProtocol


class LayerZeroLocalRunConfigBuilder:
    def build(self, data: LayerZeroLocalRunConfigInput) -> RunConfig:
        config_factory = data.config_factories.get(
            data.job.seed_name,
            data.default_config_factory,
        )
        scraper_kwargs = config_factory.create_scraper_kwargs(data.job)
        return RunConfig(
            output_dir=data.run_config.output_dir,
            include_urls=data.run_config.include_urls,
            debug_dir=data.run_config.debug_dir,
            scraper_kwargs=scraper_kwargs,
        )


@dataclass(frozen=True)
class LayerZeroJobExecutionInput:
    run_config: RunConfig
    local_run_config: RunConfig
    job: ListJobRegistryEntry
    year: int


@dataclass(frozen=True)
class LayerZeroJobExecutionResult:
    l0_raw_json_path: Path


class LayerZeroJobRunner:
    def run(self, data: LayerZeroJobExecutionInput) -> LayerZeroJobExecutionResult:
        rendered_json_path = format_domain_year_name(
            data.job.json_output_path,
            domain=data.job.output_category,
            year=data.year,
        )
        l0_raw_json_path, l0_raw_csv_path = layer_zero_raw_paths(
            output_category=data.job.output_category,
            rendered_json_path=rendered_json_path,
            csv_output_path=data.job.csv_output_path,
        )

        effective_run_config = (
            data.local_run_config
            if data.local_run_config.scraper_kwargs
            else data.run_config
        )
        ScraperRunner(effective_run_config).run_and_export(
            data.job.list_scraper_cls,
            l0_raw_json_path,
            l0_raw_csv_path,
        )
        return LayerZeroJobExecutionResult(l0_raw_json_path=l0_raw_json_path)
