# ruff: noqa: ARG002, ARG005, S108
from pathlib import Path

from scrapers.base.run_config import RunConfig
from scrapers.wiki.application import ConstructorsMirrorService
from scrapers.wiki.application import LayerOneExecutor
from layers.one.executor import LayerOneExecutorPreset
from scrapers.wiki.application import LayerZeroExecutor
from layers.zero.executor import LayerZeroExecutorPreset
from scrapers.wiki.application import LayerZeroMergeService
from layers.zero.policies import MirrorConstructorsJobHook
from layers.seed.registry import ListJobRegistryEntry
from layers.seed.registry import SeedRegistryEntry
from scrapers.base.runner import ScraperRunner


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

    executor = LayerOneExecutor(
        preset=LayerOneExecutorPreset(
            seed_registry=(supported_seed, unsupported_seed),
            validate_seed_registry=lambda registry: None,
            runners=lambda: {"drivers": _Runner()},
            engine_manufacturers_runner=lambda base_wiki_dir,
            include_urls: engine_runner_calls.append(
                (base_wiki_dir, include_urls),
            ),
        ),
    )

    run_config = RunConfig(
        output_dir=Path("/tmp"),
        include_urls=True,
        debug_dir=Path("/tmp/debug"),
    )
    executor.run(run_config, Path("/tmp/wiki"))

    assert ran_seeds == ["drivers"]
    assert engine_runner_calls == [(Path("/tmp/wiki"), True)]


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
        preset=LayerZeroExecutorPreset(
            list_job_registry=(job,),
            validate_list_registry=lambda registry: None,
            config_factories=dict,
            default_config_factory=_DefaultConfigFactory(),
            merger=merge_service,
            job_hook=MirrorConstructorsJobHook(
                constructors_mirror_service=constructors_mirror_service,
                should_mirror_predicate=(
                    lambda list_job: list_job.list_scraper_cls.__name__
                    == "CurrentConstructorsListScraper"
                ),
            ),
            year_provider=lambda: 2026,
        ),
    )

    run_config = RunConfig(
        output_dir=Path("/tmp"),
        include_urls=True,
        debug_dir=Path("/tmp/debug"),
    )
    base_wiki_dir = Path("/tmp/wiki")
    original_run_and_export = ScraperRunner.run_and_export
    ScraperRunner.run_and_export = (
        lambda self, scraper_cls, *_args, **_kwargs: run_calls.append(scraper_cls)
    )
    try:
        executor.run(run_config, base_wiki_dir)
    finally:
        ScraperRunner.run_and_export = original_run_and_export

    assert run_calls == [CurrentConstructorsListScraper]
    assert merge_calls == [base_wiki_dir]
    assert mirror_calls == [
        (
            base_wiki_dir,
            Path("/tmp/wiki/layers/0_layer/constructors/raw/f1_constructors_2026.json"),
        ),
    ]
