from pathlib import Path

from layers.one.executor import LayerOneExecutor
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
from layers.zero.executor import LayerZeroExecutor
from layers.zero.policies import NullLayerZeroJobHook
from scrapers.base.run_config import RunConfig


class _EventReporter:
    def __init__(self) -> None:
        self.events: list[tuple[str, str, str]] = []

    def started(self, *, layer: str, step: str) -> None:
        self.events.append(("started", layer, step))

    def finished(self, *, layer: str, step: str) -> None:
        self.events.append(("finished", layer, step))

    def skipped(self, *, layer: str, step: str, reason: str) -> None:
        self.events.append(("skipped", layer, f"{step}:{reason}"))


class _FakeListScraper:
    pass


class _FakeMergeService:
    def merge(self, _base_wiki_dir: Path) -> None:
        return None


class _FakeConfigFactory:
    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        return {}


class _FakeRunner:
    def __init__(self, calls: list[str]) -> None:
        self._calls = calls

    def run(self, seed: SeedRegistryEntry, _run_config: RunConfig, _base_wiki_dir: Path) -> None:
        self._calls.append(seed.seed_name)


def test_layer_one_executor_emits_reporting_events_for_started_finished_and_skipped() -> None:
    supported_seed = SeedRegistryEntry(
        seed_name="drivers",
        wikipedia_url="https://example.com",
        output_category="drivers",
        list_scraper_cls=_FakeListScraper,
        default_output_path="raw/drivers/seeds/drivers.json",
        legacy_output_path="drivers/drivers.json",
    )
    unsupported_seed = SeedRegistryEntry(
        seed_name="unsupported",
        wikipedia_url="https://example.com",
        output_category="unsupported",
        list_scraper_cls=_FakeListScraper,
        default_output_path="raw/unsupported/seeds/unsupported.json",
        legacy_output_path="unsupported/unsupported.json",
    )

    reporter = _EventReporter()
    runner_calls: list[str] = []
    engine_calls: list[tuple[Path, bool, _EventReporter]] = []

    executor = LayerOneExecutor(
        seed_registry=(supported_seed, unsupported_seed),
        validate_seed_registry_function=lambda _registry: None,
        runner_map_builder=lambda: {"drivers": _FakeRunner(runner_calls)},
        engine_manufacturers_runner=lambda *, base_wiki_dir, include_urls, reporter: engine_calls.append(
            (base_wiki_dir, include_urls, reporter),
        ),
        reporter=reporter,
    )

    executor.run(
        RunConfig(output_dir=Path("/tmp"), include_urls=True, debug_dir=Path("/tmp/debug")),
        Path("/tmp/wiki"),
    )

    assert runner_calls == ["drivers"]
    assert engine_calls == [(Path("/tmp/wiki"), True, reporter)]
    assert reporter.events == [
        ("started", "layer_one", "drivers"),
        ("finished", "layer_one", "drivers"),
        ("started", "layer_one", "unsupported"),
        ("skipped", "layer_one", "unsupported:unsupported seed"),
    ]


def test_layer_zero_executor_emits_reporting_events_for_each_job() -> None:
    job = ListJobRegistryEntry(
        seed_name="drivers",
        wikipedia_url="https://example.com",
        output_category="drivers",
        list_scraper_cls=_FakeListScraper,
        json_output_path="raw/drivers/f1_drivers_{year}.json",
        legacy_json_output_path="drivers/f1_drivers_{year}.json",
        csv_output_path="drivers/f1_drivers.csv",
    )
    reporter = _EventReporter()
    executor = LayerZeroExecutor(
        list_job_registry=(job,),
        validate_list_registry=lambda _registry: None,
        run_config_factory_map_builder=dict,
        default_config_factory=_FakeConfigFactory(),
        merge_service=_FakeMergeService(),
        job_hook=NullLayerZeroJobHook(),
        year_provider=lambda: 2026,
        reporter=reporter,
    )

    run_config = RunConfig(output_dir=Path("/tmp"), include_urls=False, debug_dir=Path("/tmp/debug"))

    original_run_single_job = LayerZeroExecutor._run_single_job
    LayerZeroExecutor._run_single_job = lambda self, **_kwargs: Path("layers/0_layer/drivers/raw/f1_drivers_2026.json")
    try:
        executor.run(run_config, Path("/tmp/wiki"))
    finally:
        LayerZeroExecutor._run_single_job = original_run_single_job

    assert reporter.events == [
        ("started", "layer_zero", "drivers"),
        ("finished", "layer_zero", "drivers"),
    ]


def test_run_engine_manufacturers_reports_started_and_finished() -> None:
    reporter = _EventReporter()

    import importlib
    import sys
    import types

    sys.modules.setdefault(
        "layers.orchestration.runners.circuits",
        types.SimpleNamespace(CircuitsRunner=object),
    )
    sys.modules.setdefault(
        "layers.orchestration.runners.constructors",
        types.SimpleNamespace(ConstructorsRunner=object),
    )
    sys.modules.setdefault(
        "layers.orchestration.runners.drivers",
        types.SimpleNamespace(DriversRunner=object),
    )
    helpers = importlib.import_module("layers.orchestration.helpers")

    original_export = helpers.export_complete_engine_manufacturers
    helpers.export_complete_engine_manufacturers = lambda **_kwargs: None
    try:
        helpers.run_engine_manufacturers(
            base_wiki_dir=Path("/tmp/wiki"),
            include_urls=False,
            reporter=reporter,
        )
    finally:
        helpers.export_complete_engine_manufacturers = original_export

    assert reporter.events == [
        ("started", "layer_one", "engine_manufacturers"),
        ("finished", "layer_one", "engine_manufacturers"),
    ]
