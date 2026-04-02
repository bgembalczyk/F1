import dataclasses
from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.debug_contract import DebugMode
from scrapers.base.debug_contract import resolve_debug_contract
from scrapers.base.logging import configure_logging
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
from scrapers.base.run_config import RunConfig


class LayerOneExecutor:
    def __init__(
        self,
        *,
        seed_registry: tuple[SeedRegistryEntry, ...],
        validate_seed_registry_function: Callable[
            [tuple[SeedRegistryEntry, ...]],
            None,
        ],
        runner_map_builder: Callable[[], dict[str, LayerOneRunnerProtocol]],
        engine_manufacturers_runner: Callable[[Path, bool], None],
    ) -> None:
        self._seed_registry = seed_registry
        self._validate_seed_registry_function = validate_seed_registry_function
        self._runner_map_builder = runner_map_builder
        self._engine_manufacturers_runner = engine_manufacturers_runner
        self._logger = get_logger(self.__class__.__name__)

    def run(self, run_config: RunConfig, base_wiki_dir: Path) -> None:
        self._validate_seed_registry_function(self._seed_registry)
        runner_map = self._runner_map_builder()
        self._validate_runner_debug_contract(runner_map)
        effective_run_config = self._normalize_run_config_for_debug_contract(run_config)
        configure_logging(debug_mode=effective_run_config.debug_mode)
        run_id = str(uuid4())

        for seed in self._seed_registry:
            context = build_execution_context(
                run_id=run_id,
                seed_name=seed.seed_name,
                domain=seed.output_category,
                source_name=getattr(
                    getattr(seed, "complete_scraper_cls", None)
                    or getattr(seed, "list_scraper_cls", None),
                    "__name__",
                    "",
                ),
            )
            self._logger.info("layer1 seed started", extra=context)

            runner = runner_map.get(seed.seed_name)
            if runner is None:
                self._logger.warning("layer1 seed skipped: unsupported", extra=context)
                continue

            runner.run(seed, effective_run_config, base_wiki_dir)
            self._logger.info("layer1 seed finished", extra=context)

        self._engine_manufacturers_runner(
            base_wiki_dir=base_wiki_dir,
            include_urls=effective_run_config.include_urls,
        )

    @staticmethod
    def _validate_runner_debug_contract(
        runner_map: dict[str, LayerOneRunnerProtocol],
    ) -> None:
        for seed_name, runner in runner_map.items():
            if getattr(runner, "DEBUG_CONTRACT_VERSION", None) != "v1":
                msg = f"Runner {seed_name!r} does not declare debug contract v1."
                raise ValueError(msg)

    @staticmethod
    def _normalize_run_config_for_debug_contract(run_config: RunConfig) -> RunConfig:
        contract = resolve_debug_contract(run_config.debug_mode)
        if contract.enforces_debug_output_path and run_config.debug_dir is None:
            msg = "debug_mode=trace requires debug_dir to be set."
            raise ValueError(msg)
        if run_config.debug_mode in {DebugMode.OFF, DebugMode.VERBOSE}:
            return dataclasses.replace(run_config, debug_dir=None)
        return run_config
