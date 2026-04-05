from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from layers.path_resolver import format_domain_year_name
from layers.zero.policies import LayerZeroJobHook
from layers.zero.policies import MirrorConstructorsJobHook
from layers.zero.policies import NullLayerZeroJobHook
from layers.zero.run_profile_paths import layer_zero_raw_paths
from scrapers.base.errors import normalize_pipeline_error
from scrapers.base.logging import RunTraceWriter
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
from scrapers.base.run_config import RunConfig
from scrapers.base.runner import ScraperRunner

if TYPE_CHECKING:
    from collections.abc import Callable
    from collections.abc import Mapping

    from layers.orchestration.protocols import LayerZeroMergeServiceProtocol
    from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
    from layers.orchestration.types import SeedName
    from layers.seed.registry.entries import ListJobRegistryEntry


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
        | Mapping[SeedName, LayerZeroRunConfigFactoryProtocol]
        | None = None,
        default_config_factory: LayerZeroRunConfigFactoryProtocol | None = None,
        merger: LayerZeroMergeServiceProtocol | None = None,
        job_hook: LayerZeroJobHook | None = None,
        year_provider: Callable[[], int] | None = None,
        run_id_provider: Callable[[], str] | None = None,
        **legacy_kwargs: object,
    ) -> None:
        run_config_factory_map_builder = legacy_kwargs.pop(
            "run_config_factory_map_builder",
            None,
        )
        merge_service = legacy_kwargs.pop("merge_service", None)
        run_and_export_function = legacy_kwargs.pop("run_and_export_function", None)
        constructors_mirror_service = legacy_kwargs.pop(
            "constructors_mirror_service",
            None,
        )
        current_constructors_scraper_name = legacy_kwargs.pop(
            "current_constructors_scraper_name",
            None,
        )
        if legacy_kwargs:
            unexpected_keys = ", ".join(sorted(legacy_kwargs))
            msg = f"Unexpected keyword arguments: {unexpected_keys}"
            raise TypeError(msg)

        self._list_job_registry = list_job_registry
        self._validate_list_registry = validate_list_registry
        if run_config_factory_map_builder is not None and config_factories is not None:
            msg = (
                "Provide only one of `config_factories` or "
                "`run_config_factory_map_builder`."
            )
            raise ValueError(msg)
        self._config_factories = config_factories or run_config_factory_map_builder

        if merge_service is not None and merger is not None:
            msg = "Provide only one of `merger` or `merge_service`."
            raise ValueError(msg)
        self._default_config_factory = default_config_factory
        self._merger = merger or merge_service
        self._run_and_export = run_and_export_function or self._run_and_export_default

        if job_hook is None and constructors_mirror_service is not None:
            job_hook = MirrorConstructorsJobHook(
                constructors_mirror_service=constructors_mirror_service,
                should_mirror_predicate=lambda job: (
                    job.list_scraper_cls.__name__ == current_constructors_scraper_name
                ),
            )
        elif job_hook is None:
            job_hook = NullLayerZeroJobHook()

        if (
            self._config_factories is None
            or self._merger is None
            or self._default_config_factory is None
            or year_provider is None
        ):
            msg = (
                "LayerZeroExecutor requires `config_factories`, "
                "`default_config_factory`, `merger`, `job_hook` "
                "and `year_provider`."
            )
            raise ValueError(msg)
        self._job_hook = job_hook
        self._year_provider = year_provider
        self._run_id_provider = run_id_provider or (lambda: str(uuid4()))
        self._logger = get_logger(self.__class__.__name__)

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_list_registry(self._list_job_registry)
        config_factories = self._resolve_config_factory()
        run_id = self._resolve_run_id(run_config)
        trace_writer = self._build_trace_writer(run_config=run_config, run_id=run_id)
        summary: dict[str, list[str]] = {"success": [], "skip": [], "fail": []}
        output_paths: list[str] = []

        for job in self._iter_jobs(run_config):
            context = build_execution_context(
                run_id=run_id,
                seed_name=job.seed_name,
                domain=job.output_category,
                source_name=job.list_scraper_cls.__name__,
                step="job",
                status="started",
            )
            self._logger.info("layer0 job started", extra=context)
            trace_writer.write(event=context | {"message": "layer0 job started"})

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
                summary["success"].append(job.seed_name)
                output_paths.append(str(l0_raw_json_path))
            except Exception as exc:
                normalized_error = normalize_pipeline_error(
                    exc,
                    code="layer0.job_failed",
                    message="Layer zero job failed.",
                    domain=job.output_category,
                    source_name=job.list_scraper_cls.__name__,
                )
                self._logger.exception(
                    "layer0 job failed",
                    extra=context
                    | {"status": "failed"}
                    | normalized_error.to_payload(),
                )
                trace_writer.write(
                    event=context
                    | {"status": "failed", "message": normalized_error.message},
                )
                summary["fail"].append(job.seed_name)
                raise normalized_error from exc

            self._logger.info(
                "layer0 job finished",
                extra=context | {"status": "success"},
            )
            trace_writer.write(
                event=context | {"status": "success", "message": "layer0 job finished"},
            )

        self._finalize_merge(base_wiki_dir)
        summary_context = build_execution_context(
            run_id=run_id,
            domain="layer0",
            source_name=self.__class__.__name__,
            step="summary",
            status="success",
        )
        self._logger.info(
            "layer0 summary: success=%d skip=%d fail=%d outputs=%s trace=%s",
            len(summary["success"]),
            len(summary["skip"]),
            len(summary["fail"]),
            output_paths,
            trace_writer.trace_path,
            extra=summary_context,
        )
        trace_writer.write(
            event=summary_context
            | {
                "success": summary["success"],
                "skip": summary["skip"],
                "fail": summary["fail"],
                "outputs": output_paths,
                "trace_path": str(trace_writer.trace_path),
            },
        )

    def _resolve_config_factory(
        self,
    ) -> dict[SeedName, LayerZeroRunConfigFactoryProtocol]:
        if callable(self._config_factories):
            return self._config_factories()
        return dict(self._config_factories)

    def _build_local_run_config(
        self,
        *,
        run_config: RunConfig,
        job: ListJobRegistryEntry,
        config_factories: dict[SeedName, LayerZeroRunConfigFactoryProtocol],
    ) -> RunConfig:
        config_factory = config_factories.get(
            job.seed_name,
            self._default_config_factory,
        )
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
        self._run_and_export(
            job.list_scraper_cls,
            l0_raw_json_path,
            l0_raw_csv_path,
            effective_run_config,
        )
        return l0_raw_json_path

    def _run_and_export_default(
        self,
        scraper_cls: type,
        json_path: Path,
        csv_path: Path | None,
        run_config: RunConfig,
    ) -> None:
        ScraperRunner(run_config).run_and_export(
            scraper_cls,
            json_path,
            csv_path,
        )

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

    def _resolve_run_id(self, run_config: RunConfig) -> str:
        if run_config.fixed_run_id:
            return run_config.fixed_run_id
        if run_config.deterministic_mode:
            return "layer0-deterministic"
        return self._run_id_provider()

    def _iter_jobs(self, run_config: RunConfig) -> tuple[ListJobRegistryEntry, ...]:
        if run_config.deterministic_mode or run_config.stable_sort:
            return tuple(
                sorted(
                    self._list_job_registry,
                    key=lambda job: (
                        job.output_category,
                        job.seed_name,
                        job.list_scraper_cls.__name__,
                    ),
                ),
            )
        return self._list_job_registry

    def _build_trace_writer(
        self,
        *,
        run_config: RunConfig,
        run_id: str,
    ) -> RunTraceWriter:
        debug_root = (
            Path(run_config.debug_dir)
            if run_config.debug_dir
            else Path(run_config.output_dir)
        )
        trace_path = debug_root / "traces" / f"layer0_{run_id}.jsonl"
        timestamp_provider = (
            (lambda: run_config.fixed_timestamp)
            if run_config.fixed_timestamp is not None
            else None
        )
        return RunTraceWriter(trace_path, timestamp_provider=timestamp_provider)
