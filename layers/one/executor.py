from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from layers.one.workers import LayerOneRunnerSelectionInput
from layers.one.workers import LayerOneRunnerSelector
from layers.one.workers import LayerOneSeedExecutionInput
from layers.one.workers import LayerOneSeedRunner
from layers.orchestration.protocols import LayerOneRunnerProtocol
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
        runner_selector: LayerOneRunnerSelector | None = None,
        seed_runner: LayerOneSeedRunner | None = None,
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
        self._runner_selector = runner_selector or LayerOneRunnerSelector()
        self._seed_runner = seed_runner or LayerOneSeedRunner()
        self._logger = get_logger(self.__class__.__name__)

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_seed_registry(self._seed_registry)
        runner_map = self._runners()
        run_id = str(uuid4())

        for seed in self._seed_registry:
            context = build_execution_context(
                run_id=run_id,
                seed_name=seed.seed_name,
                domain=seed.output_category,
                source_name=seed.complete_scraper_cls.__name__,
            )
            try:
                self._logger.info("layer1 seed started", extra=context)
                runner = self._runner_selector.select(
                    LayerOneRunnerSelectionInput(
                        seed_name=seed.seed_name,
                        runner_map=runner_map,
                    ),
                )
                if runner is None:
                    self._logger.warning(
                        "layer1 seed skipped: unsupported",
                        extra=context,
                    )
                    continue

                self._seed_runner.run(
                    LayerOneSeedExecutionInput(
                        seed=seed,
                        run_config=run_config,
                        base_wiki_dir=base_wiki_dir,
                        runner=runner,
                    ),
                )
                self._logger.info("layer1 seed finished", extra=context)
            except Exception:
                self._logger.exception("layer1 seed failed", extra=context)
                raise

        self._engine_manufacturers_runner(
            base_wiki_dir=base_wiki_dir,
            include_urls=run_config.include_urls,
        )
