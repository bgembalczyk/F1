from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.reporting import LayerJobResult
from layers.reporting import LayerRunSummary
from layers.reporting import RunSummaryBuilder
from layers.seed.registry.entries import SeedRegistryEntry
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
        runners: Callable[[], dict[str, LayerOneRunnerProtocol]] | None = None,
        runner_map_builder: Callable[[], dict[str, LayerOneRunnerProtocol]] | None = None,
        engine_manufacturers_runner: Callable[[Path, bool], None] | None = None,
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
        self._summary_builder = RunSummaryBuilder()
        self._last_summary: LayerRunSummary | None = None
        self._logger = get_logger(self.__class__.__name__)

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_seed_registry(self._seed_registry)
        runner_map = self._runners()
        run_id = str(uuid4())
        summary, timer = self._summary_builder.start(layer="layer1")

        try:
            for seed in self._seed_registry:
                context = build_execution_context(
                    run_id=run_id,
                    seed_name=seed.seed_name,
                    domain=seed.output_category,
                    source_name=seed.list_scraper_cls.__name__,
                )
                self._logger.info("layer1 seed started", extra=context)

                runner = runner_map.get(seed.seed_name)
                if runner is None:
                    self._logger.warning("layer1 seed skipped: unsupported", extra=context)
                    summary.jobs.append(
                        LayerJobResult(
                            name=seed.seed_name,
                            module=seed.list_scraper_cls.__module__,
                            status="skipped",
                            output_path=None,
                            error_code="L1_SEED_UNSUPPORTED",
                            error_detail="missing runner",
                        ),
                    )
                    continue

                try:
                    runner.run(seed, run_config, base_wiki_dir)
                except Exception as exc:
                    summary.jobs.append(
                        LayerJobResult(
                            name=seed.seed_name,
                            module=seed.list_scraper_cls.__module__,
                            status="error",
                            output_path=None,
                            error_code="L1_SEED_FAILED",
                            error_detail=str(exc),
                        ),
                    )
                    raise
                else:
                    summary.jobs.append(
                        LayerJobResult(
                            name=seed.seed_name,
                            module=seed.list_scraper_cls.__module__,
                            status="success",
                            output_path=str(
                                (base_wiki_dir / seed.default_output_path).resolve(),
                            ),
                        ),
                    )
                    self._logger.info("layer1 seed finished", extra=context)

            self._engine_manufacturers_runner(
                base_wiki_dir=base_wiki_dir,
                include_urls=run_config.include_urls,
            )
        finally:
            self._last_summary = self._summary_builder.finish(summary, timer)

    @property
    def last_summary(self) -> LayerRunSummary | None:
        return self._last_summary
