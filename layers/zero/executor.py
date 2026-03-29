from collections.abc import Callable
from pathlib import Path

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.zero.helpers import layer_zero_raw_paths
from layers.zero.merge_service import LayerZeroMergeService
from layers.zero.policies import LayerZeroJobHook
from scrapers.base.run_config import RunConfig
from scrapers.base.runner import ScraperRunner


class LayerZeroExecutor:
    def __init__(
        self,
        *,
        list_job_registry: tuple[ListJobRegistryEntry, ...],
        validate_list_registry: Callable[[tuple[ListJobRegistryEntry, ...]], None],
        run_config_factory_map_builder: Callable[
            [],
            dict[str, LayerZeroRunConfigFactoryProtocol],
        ],
        default_config_factory: LayerZeroRunConfigFactoryProtocol,
        merge_service: LayerZeroMergeService,
        job_hook: LayerZeroJobHook,
        year_provider: Callable[[], int],
    ) -> None:
        self._list_job_registry = list_job_registry
        self._validate_list_registry = validate_list_registry
        self._run_config_factory_map_builder = run_config_factory_map_builder
        self._default_config_factory = default_config_factory
        self._merge_service = merge_service
        self._job_hook = job_hook
        self._year_provider = year_provider

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_list_registry(self._list_job_registry)
        config_factories = self._resolve_config_factory()

        for job in self._list_job_registry:
            print(f"[list] running  {job.list_scraper_cls.__name__}")

            local_run_config = self._build_local_run_config(
                run_config=run_config,
                job=job,
                config_factories=config_factories,
            )
            l0_raw_json_path = self._run_single_job(
                run_config=run_config,
                local_run_config=local_run_config,
                job=job,
            )
            self._maybe_mirror_constructors(
                base_wiki_dir=base_wiki_dir,
                job=job,
                l0_raw_json_path=l0_raw_json_path,
            )

            print(f"[list] finished {job.list_scraper_cls.__name__}")

        self._finalize_merge(base_wiki_dir)

    def _resolve_config_factory(self) -> dict[str, LayerZeroRunConfigFactoryProtocol]:
        return self._run_config_factory_map_builder()

    def _build_local_run_config(
        self,
        *,
        run_config: RunConfig,
        job: ListJobRegistryEntry,
        config_factories: dict[str, LayerZeroRunConfigFactoryProtocol],
    ) -> RunConfig:
        config_factory = config_factories.get(job.seed_name, self._default_config_factory)
        scraper_kwargs = config_factory.create_scraper_kwargs(job)
        return RunConfig(
            output_dir=run_config.output_dir,
            include_urls=run_config.include_urls,
            debug_dir=run_config.debug_dir,
            scraper_kwargs=scraper_kwargs,
        )

    def _run_single_job(
        self,
        *,
        run_config: RunConfig,
        local_run_config: RunConfig,
        job: ListJobRegistryEntry,
    ) -> Path:
        rendered_json_path = job.json_output_path.format(year=self._year_provider())
        l0_raw_json_path, l0_raw_csv_path = layer_zero_raw_paths(
            output_category=job.output_category,
            rendered_json_path=rendered_json_path,
            csv_output_path=job.csv_output_path,
        )

        effective_run_config = (
            local_run_config if local_run_config.scraper_kwargs else run_config
        )
        ScraperRunner(effective_run_config).run_and_export(
            job.list_scraper_cls,
            l0_raw_json_path,
            l0_raw_csv_path,
        )
        return l0_raw_json_path

    def _maybe_mirror_constructors(
        self,
        *,
        base_wiki_dir: Path,
        job: ListJobRegistryEntry,
        l0_raw_json_path: Path,
    ) -> None:
        self._job_hook.after_job(
            base_wiki_dir=base_wiki_dir,
            job=job,
            l0_raw_json_path=l0_raw_json_path,
        )

    def _finalize_merge(self, base_wiki_dir: Path) -> None:
        self._merge_service.merge(base_wiki_dir)
