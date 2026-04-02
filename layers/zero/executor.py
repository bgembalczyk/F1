from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from layers.orchestration.protocols import LayerZeroMergeServiceProtocol
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.zero.policies import LayerZeroJobHook
from layers.zero.workers import LayerZeroConfigFactoryResolutionInput
from layers.zero.workers import LayerZeroConfigFactoryResolver
from layers.zero.workers import LayerZeroJobExecutionInput
from layers.zero.workers import LayerZeroJobRunner
from layers.zero.workers import LayerZeroLocalRunConfigBuilder
from layers.zero.workers import LayerZeroLocalRunConfigInput
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
from scrapers.base.run_config import RunConfig


class LayerZeroExecutor:
    def __init__(
        self,
        *,
        list_job_registry: tuple[ListJobRegistryEntry, ...],
        validate_list_registry: Callable[[tuple[ListJobRegistryEntry, ...]], None],
        config_factories: Callable[
            [],
            dict[str, LayerZeroRunConfigFactoryProtocol],
        ]
        | None = None,
        run_config_factory_map_builder: Callable[
            [],
            dict[str, LayerZeroRunConfigFactoryProtocol],
        ]
        | None = None,
        default_config_factory: LayerZeroRunConfigFactoryProtocol | None = None,
        merger: LayerZeroMergeServiceProtocol | None = None,
        merge_service: LayerZeroMergeServiceProtocol | None = None,
        job_hook: LayerZeroJobHook | None = None,
        year_provider: Callable[[], int] | None = None,
        config_factory_resolver: LayerZeroConfigFactoryResolver | None = None,
        local_run_config_builder: LayerZeroLocalRunConfigBuilder | None = None,
        job_runner: LayerZeroJobRunner | None = None,
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
        self._config_factory_resolver = config_factory_resolver or LayerZeroConfigFactoryResolver()
        self._local_run_config_builder = (
            local_run_config_builder or LayerZeroLocalRunConfigBuilder()
        )
        self._job_runner = job_runner or LayerZeroJobRunner()
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
            try:
                self._logger.info("layer0 job started", extra=context)
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
                self._logger.info("layer0 job finished", extra=context)
            except Exception:
                self._logger.exception("layer0 job failed", extra=context)
                raise

        self._finalize_merge(base_wiki_dir)

    def _resolve_config_factory(self) -> dict[str, LayerZeroRunConfigFactoryProtocol]:
        return self._config_factory_resolver.resolve(
            LayerZeroConfigFactoryResolutionInput(
                config_factories_builder=self._config_factories,
            ),
        )

    def _build_local_run_config(
        self,
        *,
        run_config: RunConfig,
        job: ListJobRegistryEntry,
        config_factories: dict[str, LayerZeroRunConfigFactoryProtocol],
    ) -> RunConfig:
        return self._local_run_config_builder.build(
            LayerZeroLocalRunConfigInput(
                run_config=run_config,
                job=job,
                config_factories=config_factories,
                default_config_factory=self._default_config_factory,
            ),
        )

    def _run_single_job(
        self,
        *,
        run_config: RunConfig,
        local_run_config: RunConfig,
        job: ListJobRegistryEntry,
    ) -> Path:
        return self._job_runner.run(
            LayerZeroJobExecutionInput(
                run_config=run_config,
                local_run_config=local_run_config,
                job=job,
                year=self._year_provider(),
            ),
        ).l0_raw_json_path

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
