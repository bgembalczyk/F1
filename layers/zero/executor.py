from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from layers.orchestration.protocols import LayerZeroMergeServiceProtocol
from layers.orchestration.types import SeedName
from layers.path_resolver import format_domain_year_name
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.zero.run_profile_paths import layer_zero_raw_paths
from layers.zero.policies import LayerZeroJobHook
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
from scrapers.base.run_config import RunConfig
from scrapers.base.runner import ScraperRunner
from scrapers.base.errors import normalize_pipeline_error


class LayerZeroExecutor:
    def __init__(
        self,
        *,
        list_job_registry: tuple[ListJobRegistryEntry, ...],
        validate_list_registry: Callable[[tuple[ListJobRegistryEntry, ...]], None],
        config_factories: Callable[
            [],
            dict[SeedName, LayerZeroRunConfigFactoryProtocol],
        ]
        | None = None,
        run_config_factory_map_builder: Callable[
            [],
            dict[SeedName, LayerZeroRunConfigFactoryProtocol],
        ]
        | None = None,
        default_config_factory: LayerZeroRunConfigFactoryProtocol | None = None,
        merger: LayerZeroMergeServiceProtocol | None = None,
        merge_service: LayerZeroMergeServiceProtocol | None = None,
        job_hook: LayerZeroJobHook | None = None,
        year_provider: Callable[[], int] | None = None,
    ) -> None:
        self._list_job_registry = list_job_registry
        self._validate_list_registry = validate_list_registry
        self._config_factories = config_factories or run_config_factory_map_builder
        self._default_config_factory = default_config_factory
        self._merger = merger or merge_service
        if (
            self._config_factories is None
            or self._merger is None
            or self._default_config_factory is None
            or job_hook is None
            or year_provider is None
        ):
            msg = (
                "LayerZeroExecutor requires `config_factories`, `default_config_factory`, "
                "`merger`, `job_hook` and `year_provider`."
            )
            raise ValueError(msg)
        self._job_hook = job_hook
        self._year_provider = year_provider
        self._logger = get_logger(self.__class__.__name__)

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_list_registry(self._list_job_registry)
        config_factories = self._resolve_config_factory()
        run_id = str(uuid4())

        for job in self._list_job_registry:
            context = build_execution_context(
                run_id=run_id,
                seed_name=job.seed_name,
                domain=job.output_category,
                source_name=job.list_scraper_cls.__name__,
            )
            self._logger.info("layer0 job started", extra=context)

            local_run_config = self._build_local_run_config(
                run_config=run_config,
                job=job,
                config_factories=config_factories,
            )
            try:
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
            except Exception as exc:
                normalized_error = normalize_pipeline_error(
                    exc,
                    code="layer0.job_failed",
                    message="Layer zero job failed.",
                    domain=job.output_category,
                    source_name=job.list_scraper_cls.__name__,
                )
                self._logger.error(
                    "layer0 job failed",
                    extra=context | normalized_error.to_payload(),
                )
                raise normalized_error from exc

            self._logger.info("layer0 job finished", extra=context)

        self._finalize_merge(base_wiki_dir)

    def _resolve_config_factory(self) -> dict[SeedName, LayerZeroRunConfigFactoryProtocol]:
        return self._config_factories()

    def _build_local_run_config(
        self,
        *,
        run_config: RunConfig,
        job: ListJobRegistryEntry,
        config_factories: dict[SeedName, LayerZeroRunConfigFactoryProtocol],
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
        rendered_json_path = format_domain_year_name(
            job.json_output_path,
            domain=job.output_category,
            year=self._year_provider(),
        )
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
        self._merger.merge(base_wiki_dir)
