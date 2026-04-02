from pathlib import Path

import pytest

from layers.one.executor import LayerOneExecutor
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.debug_contract import DebugMode
from scrapers.base.run_config import RunConfig


class _FakeScraper:
    pass


def _seed() -> SeedRegistryEntry:
    return SeedRegistryEntry(
        seed_name="drivers",
        wikipedia_url="https://example.com",
        output_category="drivers",
        list_scraper_cls=_FakeScraper,
        default_output_path="raw/drivers/f1_drivers.json",
        legacy_output_path="drivers/f1_drivers.json",
    )


def test_layer_one_executor_rejects_runner_without_declared_debug_contract() -> None:
    class _Runner:
        def run(self, seed: SeedRegistryEntry, run_config: RunConfig, base_wiki_dir: Path) -> None:
            return None

    executor = LayerOneExecutor(
        seed_registry=(_seed(),),
        validate_seed_registry_function=lambda _registry: None,
        runner_map_builder=lambda: {"drivers": _Runner()},
        engine_manufacturers_runner=lambda *_args, **_kwargs: None,
    )

    with pytest.raises(ValueError, match="debug contract v1"):
        executor.run(
            RunConfig(output_dir=Path("/tmp"), include_urls=True),
            Path("/tmp/wiki"),
        )


def test_layer_one_executor_requires_debug_dir_for_trace_mode() -> None:
    class _Runner:
        DEBUG_CONTRACT_VERSION = "v1"

        def run(self, seed: SeedRegistryEntry, run_config: RunConfig, base_wiki_dir: Path) -> None:
            return None

    executor = LayerOneExecutor(
        seed_registry=(_seed(),),
        validate_seed_registry_function=lambda _registry: None,
        runner_map_builder=lambda: {"drivers": _Runner()},
        engine_manufacturers_runner=lambda *_args, **_kwargs: None,
    )

    with pytest.raises(ValueError, match="debug_mode=trace requires debug_dir"):
        executor.run(
            RunConfig(
                output_dir=Path("/tmp"),
                include_urls=True,
                debug_mode=DebugMode.TRACE,
            ),
            Path("/tmp/wiki"),
        )
