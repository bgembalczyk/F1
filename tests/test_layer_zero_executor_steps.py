from pathlib import Path

from layers.orchestration.protocols import LayerZeroMergeServiceProtocol
from layers.orchestration.protocols import LayerZeroRunConfigFactoryProtocol
from layers.orchestration.runtime_config import RuntimeConfig
from layers.orchestration.factories import DefaultLayerZeroRunConfigFactory
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.zero.executor import LayerZeroExecutor
from layers.zero.merge_service import LayerZeroMergeService
from layers.zero.policies import MirrorConstructorsJobHook
from layers.zero.policies import NullLayerZeroJobHook
from scrapers.base.run_config import RunConfig
from scrapers.base.runner import ScraperRunner


class _FakeScraper:
    pass


class _FakeConfigFactory(LayerZeroRunConfigFactoryProtocol):
    def __init__(self, scraper_kwargs: dict[str, object]) -> None:
        self._scraper_kwargs = scraper_kwargs

    def create_scraper_kwargs(self, _job: ListJobRegistryEntry) -> dict[str, object]:
        return self._scraper_kwargs


class _MergeService(LayerZeroMergeServiceProtocol):
    def __init__(self) -> None:
        self.calls: list[Path] = []

    def merge(self, base_wiki_dir: Path) -> None:
        self.calls.append(base_wiki_dir)


class _Hook:
    def __init__(self) -> None:
        self.calls: list[tuple[Path, str, Path]] = []

    def after_job(
        self,
        *,
        base_wiki_dir: Path,
        job: ListJobRegistryEntry,
        l0_raw_json_path: Path,
    ) -> None:
        self.calls.append((base_wiki_dir, job.seed_name, l0_raw_json_path))


def _job(*, seed_name: str = "drivers") -> ListJobRegistryEntry:
    return ListJobRegistryEntry(
        seed_name=seed_name,
        wikipedia_url="https://example.com",
        output_category="drivers",
        list_scraper_cls=_FakeScraper,
        json_output_path="raw/drivers/f1_drivers_{year}.json",
        legacy_json_output_path="drivers/f1_drivers_{year}.json",
        csv_output_path="drivers/f1_drivers.csv",
    )


def _executor(
    *,
    run_config_factory_map_builder=None,
    default_config_factory=None,
    merge_service=None,
    job_hook=None,
) -> LayerZeroExecutor:
    return LayerZeroExecutor(
        list_job_registry=(_job(),),
        validate_list_registry=lambda _registry: None,
        run_config_factory_map_builder=(
            run_config_factory_map_builder if run_config_factory_map_builder else dict
        ),
        default_config_factory=(
            default_config_factory if default_config_factory else _FakeConfigFactory({})
        ),
        merge_service=(merge_service if merge_service else _MergeService()),
        job_hook=(job_hook if job_hook else NullLayerZeroJobHook()),
        year_provider=lambda: 2026,
    )


def _build_default_and_local_run_config(
    *,
    local_scraper_kwargs: dict[str, object] | None = None,
) -> tuple[RunConfig, RunConfig]:
    default_run_config = RunConfig(
        output_dir=Path("/tmp"),
        include_urls=False,
        debug_dir=Path("/tmp/debug"),
    )
    local_run_config = RunConfig(
        output_dir=Path("/tmp"),
        include_urls=False,
        debug_dir=Path("/tmp/debug"),
        scraper_kwargs=(local_scraper_kwargs if local_scraper_kwargs is not None else {}),
    )
    return default_run_config, local_run_config


def test_resolve_config_factory_uses_builder_result() -> None:
    expected = {"drivers": object()}
    executor = _executor(run_config_factory_map_builder=lambda: expected)

    resolved = executor._resolve_config_factory()

    assert resolved is expected


def test_protocol_contracts_are_met_by_production_implementations() -> None:
    assert isinstance(DefaultLayerZeroRunConfigFactory(), LayerZeroRunConfigFactoryProtocol)
    assert isinstance(
        LayerZeroMergeService(merge_function=lambda _base_wiki_dir: None),
        LayerZeroMergeServiceProtocol,
    )


def test_build_local_run_config_uses_seed_specific_factory() -> None:
    seed_job = _job(seed_name="drivers")
    executor = _executor(
        default_config_factory=_FakeConfigFactory({"from": "default"}),
    )

    local_run_config = executor._build_local_run_config(
        run_config=RunConfig(
            output_dir=Path("/tmp"),
            include_urls=True,
            debug_dir=Path("/tmp/debug"),
        ),
        job=seed_job,
        config_factories={"drivers": _FakeConfigFactory({"domain": "drivers"})},
    )

    assert local_run_config.scraper_kwargs == {"domain": "drivers"}


def test_run_single_job_passes_local_run_config_when_kwargs_present() -> None:
    calls: list[dict[str, object]] = []

    original_method = ScraperRunner.run_and_export

    def _capture_call(self, scraper_cls, json_path, csv_path=None) -> None:
        calls.append(
            {
                "scraper_cls": scraper_cls,
                "json_path": json_path,
                "csv_path": csv_path,
                "run_config": self._run_config,
            },
        )

    ScraperRunner.run_and_export = _capture_call
    executor = _executor()

    default_run_config, local_run_config = _build_default_and_local_run_config(
        local_scraper_kwargs={"x": 1},
    )

    try:
        json_path = executor._run_single_job(
            run_config=default_run_config,
            local_run_config=local_run_config,
            job=_job(),
        )
    finally:
        ScraperRunner.run_and_export = original_method

    assert calls[0]["scraper_cls"] is _FakeScraper
    assert calls[0]["json_path"] == Path("layers/0_layer/drivers/raw/f1_drivers_2026.json")
    assert calls[0]["run_config"] is local_run_config
    assert json_path == Path("layers/0_layer/drivers/raw/f1_drivers_2026.json")


def test_run_single_job_passes_global_run_config_when_local_kwargs_missing() -> None:
    calls: list[RunConfig] = []
    original_method = ScraperRunner.run_and_export

    def _capture_call(self, _scraper_cls, _json_path, _csv_path=None) -> None:
        calls.append(self._run_config)

    ScraperRunner.run_and_export = _capture_call
    executor = _executor()

    default_run_config, local_run_config = _build_default_and_local_run_config()

    try:
        executor._run_single_job(
            run_config=default_run_config,
            local_run_config=local_run_config,
            job=_job(),
        )
    finally:
        ScraperRunner.run_and_export = original_method

    assert calls == [default_run_config]


def test_maybe_mirror_constructors_delegates_to_hook() -> None:
    hook = _Hook()
    executor = _executor(job_hook=hook)

    executor._maybe_mirror_constructors(
        base_wiki_dir=Path("/tmp/wiki"),
        job=_job(seed_name="constructors"),
        l0_raw_json_path=Path("layers/0_layer/constructors/raw/f1_constructors_2026.json"),
    )

    assert hook.calls == [
        (
            Path("/tmp/wiki"),
            "constructors",
            Path("layers/0_layer/constructors/raw/f1_constructors_2026.json"),
        ),
    ]


def test_finalize_merge_calls_merge_service() -> None:
    merge_service = _MergeService()
    executor = _executor(merge_service=merge_service)

    executor._finalize_merge(Path("/tmp/wiki"))

    assert merge_service.calls == [Path("/tmp/wiki")]


def test_run_orchestrates_steps_in_order() -> None:
    executor = _executor()
    order: list[str] = []

    executor._resolve_config_factory = lambda: order.append("resolve") or {}
    executor._build_local_run_config = (
        lambda **_kwargs: order.append("build")
        or RunConfig(output_dir=Path("/tmp"), include_urls=True, debug_dir=Path("/tmp/debug"))
    )
    executor._run_single_job = (
        lambda **_kwargs: order.append("run")
        or Path("layers/0_layer/drivers/raw/f1_drivers_2026.json")
    )
    executor._maybe_mirror_constructors = lambda **_kwargs: order.append("mirror")
    executor._finalize_merge = lambda *_args, **_kwargs: order.append("merge")

    executor.run(
        RuntimeConfig(
            base_wiki_dir=Path("/tmp/wiki"),
            base_debug_dir=Path("/tmp/debug"),
            include_urls=True,
        ),
    )

    assert order == ["resolve", "build", "run", "mirror", "merge"]


def test_mirror_constructors_job_hook_runs_only_for_matching_job() -> None:
    mirror_calls: list[tuple[Path, Path]] = []

    class _MirrorService:
        def mirror(self, base_wiki_dir: Path, source_json_path: Path) -> None:
            mirror_calls.append((base_wiki_dir, source_json_path))

    hook = MirrorConstructorsJobHook(
        constructors_mirror_service=_MirrorService(),
        should_mirror_predicate=lambda job: job.seed_name == "constructors_current",
    )

    hook.after_job(
        base_wiki_dir=Path("/tmp/wiki"),
        job=_job(seed_name="drivers"),
        l0_raw_json_path=Path("layers/0_layer/drivers/raw/f1_drivers_2026.json"),
    )
    hook.after_job(
        base_wiki_dir=Path("/tmp/wiki"),
        job=_job(seed_name="constructors_current"),
        l0_raw_json_path=Path("layers/0_layer/constructors/raw/f1_constructors_2026.json"),
    )

    assert mirror_calls == [
        (
            Path("/tmp/wiki"),
            Path("/tmp/wiki/layers/0_layer/constructors/raw/f1_constructors_2026.json"),
        ),
    ]
