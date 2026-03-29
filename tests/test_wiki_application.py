# ruff: noqa: ARG002, ARG005, S108
from pathlib import Path

from layers.constructors_mirror_service import ConstructorsMirrorService
from layers.one.executor import LayerOneExecutor
from layers.orchestration.factories import SponsorshipLiveriesRunConfigFactory
import layers.orchestration.helpers as orchestration_helpers
from layers.orchestration.helpers import run_engine_manufacturers
from layers.zero.executor import LayerZeroExecutor
from layers.zero.merge_service import LayerZeroMergeService
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig


class _CollectingProgressReporter:
    def __init__(self) -> None:
        self.events: list[tuple[str, str, str, str | None]] = []

    def started(self, scope: str, name: str) -> None:
        self.events.append(("started", scope, name, None))

    def finished(self, scope: str, name: str) -> None:
        self.events.append(("finished", scope, name, None))

    def skipped(self, scope: str, name: str, reason: str) -> None:
        self.events.append(("skipped", scope, name, reason))

    def warn(self, scope: str, name: str, message: str) -> None:
        self.events.append(("warn", scope, name, message))


class _FakeScraper:
    pass


class CurrentConstructorsListScraper:
    pass


def test_layer_one_executor_runs_supported_job_and_skips_unsupported_job() -> None:
    supported_seed = SeedRegistryEntry(
        seed_name="drivers",
        wikipedia_url="https://example.com",
        output_category="drivers",
        list_scraper_cls=_FakeScraper,
        default_output_path="raw/drivers/seeds/drivers.json",
        legacy_output_path="drivers/drivers.json",
    )
    unsupported_seed = SeedRegistryEntry(
        seed_name="unsupported",
        wikipedia_url="https://example.com",
        output_category="unsupported",
        list_scraper_cls=_FakeScraper,
        default_output_path="raw/unsupported/seeds/unsupported.json",
        legacy_output_path="unsupported/unsupported.json",
    )

    ran_seeds: list[str] = []

    class _Runner:
        def run(
            self,
            seed: SeedRegistryEntry,
            run_config: RunConfig,
            base_wiki_dir: Path,
        ) -> None:
            ran_seeds.append(seed.seed_name)

    engine_runner_calls: list[tuple[Path, bool]] = []
    reporter = _CollectingProgressReporter()

    executor = LayerOneExecutor(
        seed_registry=(supported_seed, unsupported_seed),
        validate_seed_registry_function=lambda registry: None,
        runner_map_builder=lambda: {"drivers": _Runner()},
        engine_manufacturers_runner=lambda base_wiki_dir,
        include_urls: engine_runner_calls.append(
            (base_wiki_dir, include_urls),
        ),
        progress_reporter=reporter,
    )

    run_config = RunConfig(
        output_dir=Path("/tmp"),
        include_urls=True,
        debug_dir=Path("/tmp/debug"),
    )
    executor.run(run_config, Path("/tmp/wiki"))

    assert ran_seeds == ["drivers"]
    assert engine_runner_calls == [(Path("/tmp/wiki"), True)]
    assert reporter.events == [
        ("started", "complete", "drivers", None),
        ("finished", "complete", "drivers", None),
        ("started", "complete", "unsupported", None),
        ("skipped", "complete", "unsupported", "unsupported seed"),
    ]


def test_constructors_mirror_service_mirrors_json_to_targets(tmp_path: Path) -> None:
    source_json_path = (
        tmp_path
        / "data"
        / "wiki"
        / "layers"
        / "0_layer"
        / "constructors"
        / "raw"
        / "f1_constructors_2026.json"
    )
    source_json_path.parent.mkdir(parents=True, exist_ok=True)
    source_json_path.write_text("{}", encoding="utf-8")

    copied_targets: list[Path] = []

    def _copy_file(source: Path, target: Path) -> None:
        copied_targets.append(target)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    mirror_service = ConstructorsMirrorService(
        mirror_targets=(
            ("chassis_constructors", "f1_constructors_{year}.json"),
            ("constructors", "f1_constructors_{year}.json"),
            ("teams", "f1_constructors_{year}.json"),
        ),
        copy_file=_copy_file,
        year_provider=lambda: 2026,
    )

    mirror_service.mirror(tmp_path / "data" / "wiki", source_json_path)

    assert copied_targets == [
        tmp_path
        / "data"
        / "wiki"
        / "layers"
        / "0_layer"
        / "chassis_constructors"
        / "raw"
        / "f1_constructors_2026.json",
        tmp_path
        / "data"
        / "wiki"
        / "layers"
        / "0_layer"
        / "teams"
        / "raw"
        / "f1_constructors_2026.json",
    ]


def test_layer_zero_executor_runs_merge_after_jobs() -> None:
    merge_calls: list[Path] = []
    merge_service = LayerZeroMergeService(
        merge_function=lambda base_wiki_dir: merge_calls.append(base_wiki_dir),
    )

    run_calls: list[type] = []

    job = ListJobRegistryEntry(
        seed_name="constructors_current",
        wikipedia_url="https://example.com",
        output_category="constructors",
        list_scraper_cls=CurrentConstructorsListScraper,
        json_output_path="raw/constructors/list/f1_constructors_{year}.json",
        legacy_json_output_path="constructors/f1_constructors_{year}.json",
    )

    mirror_calls: list[tuple[Path, Path]] = []
    constructors_mirror_service = ConstructorsMirrorService(
        mirror_targets=(("teams", "f1_constructors_{year}.json"),),
        copy_file=lambda source, target: None,
        year_provider=lambda: 2026,
    )
    constructors_mirror_service.mirror = (
        lambda base_wiki_dir, source_json_path: mirror_calls.append(
            (base_wiki_dir, source_json_path),
        )
    )

    class _DefaultConfigFactory:
        def create_scraper_kwargs(
            self,
            list_job: ListJobRegistryEntry,
        ) -> dict[str, object]:
            return {}

    executor = LayerZeroExecutor(
        list_job_registry=(job,),
        validate_list_registry=lambda registry: None,
        run_config_factory_map_builder=dict,
        default_config_factory=_DefaultConfigFactory(),
        run_and_export_function=lambda scraper_cls, *_args, **_kwargs: run_calls.append(
            scraper_cls,
        ),
        constructors_mirror_service=constructors_mirror_service,
        merge_service=merge_service,
        current_constructors_scraper_name="CurrentConstructorsListScraper",
        year_provider=lambda: 2026,
        progress_reporter=_CollectingProgressReporter(),
    )

    run_config = RunConfig(
        output_dir=Path("/tmp"),
        include_urls=True,
        debug_dir=Path("/tmp/debug"),
    )
    base_wiki_dir = Path("/tmp/wiki")
    executor.run(run_config, base_wiki_dir)

    assert run_calls == [CurrentConstructorsListScraper]
    assert merge_calls == [base_wiki_dir]
    assert mirror_calls == [
        (
            base_wiki_dir,
            Path("/tmp/wiki/layers/0_layer/constructors/raw/f1_constructors_2026.json"),
        ),
    ]


def test_layer_zero_executor_emits_progress_events() -> None:
    reporter = _CollectingProgressReporter()
    merge_service = LayerZeroMergeService(merge_function=lambda _base_wiki_dir: None)

    job = ListJobRegistryEntry(
        seed_name="constructors_current",
        wikipedia_url="https://example.com",
        output_category="constructors",
        list_scraper_cls=CurrentConstructorsListScraper,
        json_output_path="raw/constructors/list/f1_constructors_{year}.json",
        legacy_json_output_path="constructors/f1_constructors_{year}.json",
    )

    class _DefaultConfigFactory:
        def create_scraper_kwargs(
            self,
            _list_job: ListJobRegistryEntry,
        ) -> dict[str, object]:
            return {}

    executor = LayerZeroExecutor(
        list_job_registry=(job,),
        validate_list_registry=lambda registry: None,
        run_config_factory_map_builder=dict,
        default_config_factory=_DefaultConfigFactory(),
        run_and_export_function=lambda *_args, **_kwargs: None,
        constructors_mirror_service=ConstructorsMirrorService(
            mirror_targets=(("teams", "f1_constructors_{year}.json"),),
            copy_file=lambda _source, _target: None,
            year_provider=lambda: 2026,
        ),
        merge_service=merge_service,
        current_constructors_scraper_name="CurrentConstructorsListScraper",
        year_provider=lambda: 2026,
        progress_reporter=reporter,
    )

    executor.run(
        RunConfig(output_dir=Path("/tmp"), include_urls=False, debug_dir=Path("/tmp/debug")),
        Path("/tmp/wiki"),
    )

    assert reporter.events == [
        ("started", "list", "CurrentConstructorsListScraper", None),
        ("finished", "list", "CurrentConstructorsListScraper", None),
    ]


def test_sponsorship_liveries_factory_emits_warning_when_gemini_key_missing() -> None:
    reporter = _CollectingProgressReporter()
    factory = SponsorshipLiveriesRunConfigFactory(progress_reporter=reporter)

    kwargs = factory.create_scraper_kwargs(
        ListJobRegistryEntry(
            seed_name="sponsorship_liveries",
            wikipedia_url="https://example.com",
            output_category="sponsorship_liveries",
            list_scraper_cls=_FakeScraper,
            json_output_path="raw/sponsorship_liveries/list/f1_sponsorship_liveries_{year}.json",
            legacy_json_output_path="sponsorship_liveries/f1_sponsorship_liveries_{year}.json",
        ),
    )

    assert kwargs == {}
    assert reporter.events
    assert reporter.events[0][0:3] == ("warn", "main", "Gemini ParenClassifier")


def test_run_engine_manufacturers_emits_progress_events(tmp_path: Path) -> None:
    reporter = _CollectingProgressReporter()
    export_calls: list[tuple[Path, bool]] = []
    original_export = orchestration_helpers.export_complete_engine_manufacturers
    orchestration_helpers.export_complete_engine_manufacturers = (
        lambda output_dir, include_urls: export_calls.append((output_dir, include_urls))
    )
    try:
        run_engine_manufacturers(
            base_wiki_dir=tmp_path,
            include_urls=False,
            progress_reporter=reporter,
        )
    finally:
        orchestration_helpers.export_complete_engine_manufacturers = original_export

    assert export_calls == [(tmp_path / "engines/complete_engine_manufacturers", False)]
    assert reporter.events == [
        ("started", "complete", "F1CompleteEngineManufacturerDataExtractor", None),
        ("finished", "complete", "F1CompleteEngineManufacturerDataExtractor", None),
    ]
