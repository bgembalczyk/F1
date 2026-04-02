from collections.abc import Callable
from pathlib import Path
from uuid import uuid4

from layers.orchestration.protocols import LayerOneRunnerProtocol
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.logging import build_execution_context
from scrapers.base.logging import get_logger
from scrapers.base.run_config import RunConfig
from scrapers.base.errors import normalize_pipeline_error


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
                source=seed.complete_scraper_cls.__name__,
            )
            self._logger.info("job_start", extra=context)

            runner = runner_map.get(seed.seed_name)
            if runner is None:
                self._logger.warning("job_skip", extra=context)
                continue

            try:
                runner.run(seed, run_config, base_wiki_dir)
            except Exception as exc:
                normalized_error = normalize_pipeline_error(
                    exc,
                    code="layer1.seed_failed",
                    message="Layer one seed failed.",
                    domain=seed.output_category,
                    source_name=seed.complete_scraper_cls.__name__,
                )
                self._logger.error(
                    "layer1 seed failed",
                    extra=context | normalized_error.to_payload(),
                )
                raise normalized_error from exc
            self._logger.info("layer1 seed finished", extra=context)

        try:
            self._engine_manufacturers_runner(
                base_wiki_dir=base_wiki_dir,
                include_urls=run_config.include_urls,
            )
        except Exception as exc:
            normalized_error = normalize_pipeline_error(
                exc,
                code="layer1.engine_manufacturers_failed",
                message="Layer one engine manufacturers export failed.",
                domain="engines",
                source_name="F1CompleteEngineManufacturerDataExtractor",
            )
            self._logger.error(
                "layer1 engine manufacturers failed",
                extra=normalized_error.to_payload(),
            )
            raise normalized_error from exc
