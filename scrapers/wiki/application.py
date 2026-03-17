from __future__ import annotations

import shutil
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import TYPE_CHECKING

from scrapers.base.run_config import RunConfig
from scrapers.base.run_profiles import RunPathConfig
from scrapers.base.run_profiles import RunProfileName
from scrapers.base.run_profiles import build_run_profile

if TYPE_CHECKING:
    from collections.abc import Callable

    from scrapers.wiki.seed_registry import ListJobRegistryEntry
    from scrapers.wiki.seed_registry import SeedRegistryEntry


class ConstructorsMirrorService:
    def __init__(
        self,
        *,
        mirror_targets: tuple[tuple[str, str], ...],
        copy_file: Callable[[Path, Path], None],
        year_provider: Callable[[], int],
    ) -> None:
        self._mirror_targets = mirror_targets
        self._copy_file = copy_file
        self._year_provider = year_provider

    def mirror(self, base_wiki_dir: Path, source_json_path: Path) -> None:
        current_year = self._year_provider()
        for target_category, target_name_template in self._mirror_targets:
            target_path = (
                base_wiki_dir
                / "layers"
                / "0_layer"
                / target_category
                / "raw"
                / target_name_template.format(year=current_year)
            )

            if target_path == source_json_path:
                continue

            target_path.parent.mkdir(parents=True, exist_ok=True)
            self._copy_file(source_json_path, target_path)


class LayerZeroMergeService:
    def __init__(self, *, merge_function: Callable[[Path], None]) -> None:
        self._merge_function = merge_function

    def merge(self, base_wiki_dir: Path) -> None:
        self._merge_function(base_wiki_dir)


class LayerZeroExecutor:
    def __init__(
        self,
        *,
        list_job_registry: tuple[ListJobRegistryEntry, ...],
        validate_list_registry: Callable[[tuple[ListJobRegistryEntry, ...]], None],
        run_config_factory_map_builder: Callable[[], dict[str, object]],
        default_config_factory: object,
        run_and_export_function: Callable[..., None],
        constructors_mirror_service: ConstructorsMirrorService,
        merge_service: LayerZeroMergeService,
        current_constructors_scraper_name: str,
        year_provider: Callable[[], int],
    ) -> None:
        self._list_job_registry = list_job_registry
        self._validate_list_registry = validate_list_registry
        self._run_config_factory_map_builder = run_config_factory_map_builder
        self._default_config_factory = default_config_factory
        self._run_and_export_function = run_and_export_function
        self._constructors_mirror_service = constructors_mirror_service
        self._merge_service = merge_service
        self._current_constructors_scraper_name = current_constructors_scraper_name
        self._year_provider = year_provider

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_list_registry(self._list_job_registry)

        config_factories = self._run_config_factory_map_builder()

        for job in self._list_job_registry:
            print(f"[list] running  {job.list_scraper_cls.__name__}")

            config_factory = config_factories.get(
                job.seed_name,
                self._default_config_factory,
            )
            scraper_kwargs = config_factory.create_scraper_kwargs(job)

            rendered_json_path = job.json_output_path.format(year=self._year_provider())
            local_run_config = RunConfig(
                output_dir=run_config.output_dir,
                include_urls=run_config.include_urls,
                debug_dir=run_config.debug_dir,
                scraper_kwargs=scraper_kwargs,
            )

            l0_raw_json_path = (
                Path("layers")
                / "0_layer"
                / job.output_category
                / "raw"
                / Path(rendered_json_path).name
            )
            l0_raw_csv_path: Path | None = None
            if job.csv_output_path:
                l0_raw_csv_path = (
                    Path("layers")
                    / "0_layer"
                    / job.output_category
                    / "raw"
                    / Path(job.csv_output_path).name
                )

            self._run_and_export_function(
                job.list_scraper_cls,
                l0_raw_json_path,
                l0_raw_csv_path,
                run_config=local_run_config if scraper_kwargs else run_config,
            )

            if job.list_scraper_cls.__name__ == self._current_constructors_scraper_name:
                source_json_path = base_wiki_dir / l0_raw_json_path
                self._constructors_mirror_service.mirror(
                    base_wiki_dir,
                    source_json_path,
                )

            print(f"[list] finished {job.list_scraper_cls.__name__}")

        self._merge_service.merge(base_wiki_dir)


class LayerOneExecutor:
    def __init__(
        self,
        *,
        seed_registry: tuple[SeedRegistryEntry, ...],
        validate_seed_registry_function: Callable[
            [tuple[SeedRegistryEntry, ...]],
            None,
        ],
        runner_map_builder: Callable[[], dict[str, object]],
        engine_manufacturers_runner: Callable[[Path, bool], None],
    ) -> None:
        self._seed_registry = seed_registry
        self._validate_seed_registry_function = validate_seed_registry_function
        self._runner_map_builder = runner_map_builder
        self._engine_manufacturers_runner = engine_manufacturers_runner

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_seed_registry_function(self._seed_registry)
        runner_map = self._runner_map_builder()

        for seed in self._seed_registry:
            print(f"[complete] running  {seed.seed_name}")

            runner = runner_map.get(seed.seed_name)
            if runner is None:
                print(f"[complete] skipping unsupported seed: {seed.seed_name}")
                continue

            runner.run(seed, run_config, base_wiki_dir)
            print(f"[complete] finished {seed.seed_name}")

        self._engine_manufacturers_runner(
            base_wiki_dir=base_wiki_dir,
            include_urls=run_config.include_urls,
        )


class WikiPipelineApplication:
    def __init__(
        self,
        *,
        base_wiki_dir: Path,
        base_debug_dir: Path,
        layer_zero_executor: LayerZeroExecutor,
        layer_one_executor: LayerOneExecutor,
    ) -> None:
        self._base_wiki_dir = base_wiki_dir
        self._base_debug_dir = base_debug_dir
        self._layer_zero_executor = layer_zero_executor
        self._layer_one_executor = layer_one_executor

    def run_layer_zero(self) -> None:
        run_config = build_run_profile(
            RunProfileName.DEBUG,
            paths=RunPathConfig(
                wiki_output_dir=self._base_wiki_dir,
                debug_dir=self._base_debug_dir,
            ),
        )
        self._layer_zero_executor.run(run_config, self._base_wiki_dir)

    def run_layer_one(self) -> None:
        run_config = build_run_profile(
            RunProfileName.DEBUG,
            paths=RunPathConfig(
                wiki_output_dir=self._base_wiki_dir,
                debug_dir=self._base_debug_dir,
            ),
        )
        self._layer_one_executor.run(run_config, self._base_wiki_dir)


def _current_year() -> int:
    return datetime.now(tz=timezone.utc).year


def create_default_wiki_pipeline_application(
    *,
    base_wiki_dir: Path,
    base_debug_dir: Path,
) -> WikiPipelineApplication:
    from scrapers.base.helpers.runner import run_and_export
    from scrapers.wiki.layer_zero_merge import merge_layer_zero_raw_outputs
    from scrapers.wiki.orchestration import DefaultLayerZeroRunConfigFactory
    from scrapers.wiki.orchestration import build_layer_one_runner_map
    from scrapers.wiki.orchestration import build_layer_zero_run_config_factory_map
    from scrapers.wiki.orchestration import run_engine_manufacturers
    from scrapers.wiki.seed_registry import WIKI_LIST_JOB_REGISTRY
    from scrapers.wiki.seed_registry import WIKI_SEED_REGISTRY
    from scrapers.wiki.seed_registry import validate_list_job_registry
    from scrapers.wiki.seed_registry import validate_seed_registry

    constructors_mirror_service = ConstructorsMirrorService(
        mirror_targets=(
            ("chassis_constructors", "f1_constructors_{year}.json"),
            ("constructors", "f1_constructors_{year}.json"),
            ("teams", "f1_constructors_{year}.json"),
        ),
        copy_file=shutil.copy2,
        year_provider=_current_year,
    )

    layer_zero_executor = LayerZeroExecutor(
        list_job_registry=WIKI_LIST_JOB_REGISTRY,
        validate_list_registry=validate_list_job_registry,
        run_config_factory_map_builder=build_layer_zero_run_config_factory_map,
        default_config_factory=DefaultLayerZeroRunConfigFactory(),
        run_and_export_function=run_and_export,
        constructors_mirror_service=constructors_mirror_service,
        merge_service=LayerZeroMergeService(
            merge_function=merge_layer_zero_raw_outputs,
        ),
        current_constructors_scraper_name="CurrentConstructorsListScraper",
        year_provider=_current_year,
    )

    layer_one_executor = LayerOneExecutor(
        seed_registry=WIKI_SEED_REGISTRY,
        validate_seed_registry_function=validate_seed_registry,
        runner_map_builder=build_layer_one_runner_map,
        engine_manufacturers_runner=run_engine_manufacturers,
    )

    return WikiPipelineApplication(
        base_wiki_dir=base_wiki_dir,
        base_debug_dir=base_debug_dir,
        layer_zero_executor=layer_zero_executor,
        layer_one_executor=layer_one_executor,
    )
