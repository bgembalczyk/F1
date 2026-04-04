import inspect
from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.orchestration.types import SeedName
from layers.seed.registry import SeedRegistryEntry
from scrapers.base.errors import normalize_pipeline_error
from scrapers.base.logging import RunTraceWriter
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
from scrapers.base.run_config import RunConfig


class LayerOneExecutor:
    def __init__(
        self,
        *,
        seed_registry: tuple[SeedRegistryEntry, ...],
        validate_seed_registry: Callable[
            [tuple[SeedRegistryEntry, ...]],
            None,
        ]
        | None = None,
        validate_seed_registry_function: Callable[
            [tuple[SeedRegistryEntry, ...]],
            None,
        ]
        | None = None,
        runners: Callable[[], dict[SeedName, LayerOneRunnerProtocol]] | None = None,
        runner_map_builder: Callable[
            [],
            dict[SeedName, LayerOneRunnerProtocol],
        ]
        | None = None,
        engine_manufacturers_runner: Callable[[Path, bool], None] | None = None,
        run_id_provider: Callable[[], str] | None = None,
    ) -> None:
        self._seed_registry = seed_registry
        self._validate_seed_registry = (
            validate_seed_registry or validate_seed_registry_function
        )
        self._runners = runners or runner_map_builder
        if (
            self._validate_seed_registry is None
            or self._runners is None
            or engine_manufacturers_runner is None
        ):
            msg = (
                "LayerOneExecutor requires `validate_seed_registry`, `runners` "
                "and `engine_manufacturers_runner`."
            )
            raise ValueError(msg)
        self._engine_manufacturers_runner = engine_manufacturers_runner
        self._run_id_provider = run_id_provider or (lambda: str(uuid4()))
        self._logger = get_logger(self.__class__.__name__)

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        run_id, trace_writer, summary, output_paths, runner_map = (
            self._prepare_execution_inputs(run_config)
        )
        self._execute_pipeline_steps(
            run_config=run_config,
            base_wiki_dir=base_wiki_dir,
            run_id=run_id,
            trace_writer=trace_writer,
            summary=summary,
            output_paths=output_paths,
            runner_map=runner_map,
        )
        self._finalize_run(
            run_id=run_id,
            trace_writer=trace_writer,
            summary=summary,
            output_paths=output_paths,
        )

    def _prepare_execution_inputs(
        self,
        run_config: RunConfig,
    ) -> tuple[
        str,
        RunTraceWriter,
        dict[str, list[str]],
        list[str],
        dict[SeedName, LayerOneRunnerProtocol],
    ]:
        self._validate_seed_registry(self._seed_registry)
        runner_map = self._runners()
        run_id = self._resolve_run_id(run_config)
        trace_writer = self._build_trace_writer(run_config=run_config, run_id=run_id)
        summary: dict[str, list[str]] = {"success": [], "skip": [], "fail": []}
        output_paths: list[str] = []
        return run_id, trace_writer, summary, output_paths, runner_map

    def _execute_pipeline_steps(
        self,
        *,
        run_config: RunConfig,
        base_wiki_dir: Path,
        run_id: str,
        trace_writer: RunTraceWriter,
        summary: dict[str, list[str]],
        output_paths: list[str],
        runner_map: dict[SeedName, LayerOneRunnerProtocol],
    ) -> None:
        for seed in self._iter_seeds(run_config):
            self._run_single_seed(
                seed=seed,
                run_config=run_config,
                base_wiki_dir=base_wiki_dir,
                run_id=run_id,
                trace_writer=trace_writer,
                summary=summary,
                output_paths=output_paths,
                runner_map=runner_map,
            )
        self._run_engine_manufacturers_step(
            run_config=run_config,
            base_wiki_dir=base_wiki_dir,
            run_id=run_id,
            summary=summary,
            output_paths=output_paths,
        )

    def _run_single_seed(
        self,
        *,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
        run_id: str,
        trace_writer: RunTraceWriter,
        summary: dict[str, list[str]],
        output_paths: list[str],
        runner_map: dict[SeedName, LayerOneRunnerProtocol],
    ) -> None:
        scraper_cls = getattr(seed, "complete_scraper_cls", seed.list_scraper_cls)
        context = build_execution_context(
            run_id=run_id,
            seed_name=seed.seed_name,
            domain=seed.output_category,
            source_name=scraper_cls.__name__,
            step="seed",
            status="started",
        )
        self._logger.info("layer1 seed started", extra=context)
        trace_writer.write(event=context | {"message": "layer1 seed started"})

        runner = runner_map.get(seed.seed_name)
        if runner is None:
            self._log_unsupported_seed(context=context, trace_writer=trace_writer)
            summary["skip"].append(seed.seed_name)
            return

        self._run_seed_with_error_handling(
            runner=runner,
            seed=seed,
            run_config=run_config,
            base_wiki_dir=base_wiki_dir,
            context=context,
            trace_writer=trace_writer,
            summary=summary,
            output_paths=output_paths,
            source_name=scraper_cls.__name__,
        )

    def _log_unsupported_seed(
        self,
        *,
        context: dict[str, str],
        trace_writer: RunTraceWriter,
    ) -> None:
        self._logger.warning(
            "layer1 seed skipped: unsupported",
            extra=context | {"status": "skipped"},
        )
        trace_writer.write(
            event=context
            | {
                "status": "skipped",
                "message": "layer1 seed skipped: unsupported",
            },
        )

    def _run_seed_with_error_handling(
        self,
        *,
        runner: LayerOneRunnerProtocol,
        seed: SeedRegistryEntry,
        run_config: RunConfig,
        base_wiki_dir: Path,
        context: dict[str, str],
        trace_writer: RunTraceWriter,
        summary: dict[str, list[str]],
        output_paths: list[str],
        source_name: str,
    ) -> None:
        try:
            runner.run(seed, run_config, base_wiki_dir)
            output_paths.append(seed.default_output_path)
            summary["success"].append(seed.seed_name)
        except Exception as exc:
            normalized_error = normalize_pipeline_error(
                exc,
                code="layer1.seed_failed",
                message="Layer one seed failed.",
                domain=seed.output_category,
                source_name=source_name,
            )
            self._logger.exception(
                "layer1 seed failed",
                extra=context | {"status": "failed"} | normalized_error.to_payload(),
            )
            trace_writer.write(
                event=context | {"status": "failed", "message": normalized_error.message},
            )
            summary["fail"].append(seed.seed_name)
            raise normalized_error from exc
        self._logger.info("layer1 seed finished", extra=context | {"status": "success"})
        trace_writer.write(
            event=context | {"status": "success", "message": "layer1 seed finished"},
        )

    def _run_engine_manufacturers_step(
        self,
        *,
        run_config: RunConfig,
        base_wiki_dir: Path,
        run_id: str,
        summary: dict[str, list[str]],
        output_paths: list[str],
    ) -> None:
        try:
            self._run_engine_manufacturers(
                base_wiki_dir=base_wiki_dir,
                include_urls=run_config.include_urls,
                run_id=run_id,
            )
            summary["success"].append("engine_manufacturers")
            output_paths.append(
                str(base_wiki_dir / "engines/complete_engine_manufacturers"),
            )
        except Exception as exc:
            self._handle_engine_manufacturers_failure(
                exc=exc,
                run_id=run_id,
                summary=summary,
            )

    def _handle_engine_manufacturers_failure(
        self,
        *,
        exc: Exception,
        run_id: str,
        summary: dict[str, list[str]],
    ) -> None:
        normalized_error = normalize_pipeline_error(
            exc,
            code="layer1.engine_manufacturers_failed",
            message="Layer one engine manufacturers export failed.",
            domain="engines",
            source_name="F1CompleteEngineManufacturerDataExtractor",
        )
        self._logger.exception(
            "layer1 engine manufacturers failed",
            extra=build_execution_context(
                run_id=run_id,
                seed_name="engine_manufacturers",
                domain="engines",
                source_name="F1CompleteEngineManufacturerDataExtractor",
                step="seed",
                status="failed",
            )
            | normalized_error.to_payload(),
        )
        summary["fail"].append("engine_manufacturers")
        raise normalized_error from exc

    def _finalize_run(
        self,
        *,
        run_id: str,
        trace_writer: RunTraceWriter,
        summary: dict[str, list[str]],
        output_paths: list[str],
    ) -> None:
        summary_context = build_execution_context(
            run_id=run_id,
            domain="layer1",
            source_name=self.__class__.__name__,
            step="summary",
            status="success",
        )
        self._logger.info(
            "layer1 summary: success=%d skip=%d fail=%d outputs=%s trace=%s",
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
        trace_path = debug_root / "traces" / f"layer1_{run_id}.jsonl"
        timestamp_provider = (
            (lambda: run_config.fixed_timestamp)
            if run_config.fixed_timestamp is not None
            else None
        )
        return RunTraceWriter(trace_path, timestamp_provider=timestamp_provider)

    def _resolve_run_id(self, run_config: RunConfig) -> str:
        if run_config.fixed_run_id:
            return run_config.fixed_run_id
        if run_config.deterministic_mode:
            return "layer1-deterministic"
        return self._run_id_provider()

    def _iter_seeds(self, run_config: RunConfig) -> tuple[SeedRegistryEntry, ...]:
        if run_config.deterministic_mode or run_config.stable_sort:
            return tuple(
                sorted(
                    self._seed_registry,
                    key=lambda seed: (
                        seed.output_category,
                        seed.seed_name,
                        seed.list_scraper_cls.__name__,
                    ),
                ),
            )
        return self._seed_registry

    def _run_engine_manufacturers(
        self,
        *,
        base_wiki_dir: Path,
        include_urls: bool,
        run_id: str,
    ) -> None:
        signature = inspect.signature(self._engine_manufacturers_runner)
        if "run_id" in signature.parameters:
            self._engine_manufacturers_runner(
                base_wiki_dir=base_wiki_dir,
                include_urls=include_urls,
                run_id=run_id,
            )
            return
        self._engine_manufacturers_runner(
            base_wiki_dir=base_wiki_dir,
            include_urls=include_urls,
        )
