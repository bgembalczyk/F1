from __future__ import annotations

from pathlib import Path

from layers.one.executor import LayerOneExecutor
from layers.orchestration.reporter import PipelineStepReporterProtocol
from layers.seed.registry.entries import ListJobRegistryEntry
from layers.seed.registry.entries import SeedRegistryEntry
from layers.zero.executor import LayerZeroExecutor
from layers.zero.policies import NullLayerZeroJobHook
from scrapers.base.run_config import RunConfig


class _CollectingReporter(PipelineStepReporterProtocol):
    def __init__(self) -> None:
        self.events: list[dict[str, str]] = []

    def start(self, *, layer: str, step_type: str, step_name: str) -> None:
        self.events.append(
            {
                "phase": "start",
                "layer": layer,
                "step_type": step_type,
                "step_name": step_name,
            },
        )

    def finish(self, *, layer: str, step_type: str, step_name: str) -> None:
        self.events.append(
            {
                "phase": "finish",
                "layer": layer,
                "step_type": step_type,
                "step_name": step_name,
            },
        )

    def skip(
        self,
        *,
        layer: str,
        step_type: str,
        step_name: str,
        reason: str,
    ) -> None:
        self.events.append(
            {
                "phase": "skip",
                "layer": layer,
                "step_type": step_type,
                "step_name": step_name,
                "reason": reason,
            },
        )


class _FakeListScraper:
    pass


def test_layer_one_event_contract_emits_start_skip_finish_with_shared_reporter() -> None:
    reporter = _CollectingReporter()
    supported_seed = SeedRegistryEntry(
        seed_name="drivers",
        wikipedia_url="https://example.com/drivers",
        output_category="drivers",
        list_scraper_cls=_FakeListScraper,
        default_output_path="raw/drivers/seeds/drivers.json",
        legacy_output_path="drivers/drivers.json",
    )
    unsupported_seed = SeedRegistryEntry(
        seed_name="unsupported",
        wikipedia_url="https://example.com/unsupported",
        output_category="unsupported",
        list_scraper_cls=_FakeListScraper,
        default_output_path="raw/unsupported/seeds/unsupported.json",
        legacy_output_path="unsupported/unsupported.json",
    )

    executor = LayerOneExecutor(
        seed_registry=(supported_seed, unsupported_seed),
        validate_seed_registry_function=lambda _registry: None,
        runner_map_builder=lambda: {
            "drivers": type(
                "_Runner",
                (),
                {
                    "run": lambda self, seed, run_config, base_wiki_dir: None,
                },
            )(),
        },
        engine_manufacturers_runner=(
            lambda *, base_wiki_dir, include_urls, step_reporter: (
                step_reporter.start(
                    layer="layer_one",
                    step_type="seed",
                    step_name="F1CompleteEngineManufacturerDataExtractor",
                ),
                step_reporter.finish(
                    layer="layer_one",
                    step_type="seed",
                    step_name="F1CompleteEngineManufacturerDataExtractor",
                ),
            )
        ),
        step_reporter=reporter,
    )

    executor.run(
        RunConfig(output_dir=Path("/tmp"), include_urls=True, debug_dir=Path("/tmp/debug")),
        Path("/tmp/wiki"),
    )

    assert reporter.events == [
        {
            "phase": "start",
            "layer": "layer_one",
            "step_type": "seed",
            "step_name": "drivers",
        },
        {
            "phase": "finish",
            "layer": "layer_one",
            "step_type": "seed",
            "step_name": "drivers",
        },
        {
            "phase": "start",
            "layer": "layer_one",
            "step_type": "seed",
            "step_name": "unsupported",
        },
        {
            "phase": "skip",
            "layer": "layer_one",
            "step_type": "seed",
            "step_name": "unsupported",
            "reason": "unsupported-seed",
        },
        {
            "phase": "start",
            "layer": "layer_one",
            "step_type": "seed",
            "step_name": "F1CompleteEngineManufacturerDataExtractor",
        },
        {
            "phase": "finish",
            "layer": "layer_one",
            "step_type": "seed",
            "step_name": "F1CompleteEngineManufacturerDataExtractor",
        },
    ]


def test_layer_zero_event_contract_emits_start_and_finish_for_list_job() -> None:
    reporter = _CollectingReporter()

    job = ListJobRegistryEntry(
        seed_name="drivers",
        wikipedia_url="https://example.com/drivers",
        output_category="drivers",
        list_scraper_cls=_FakeListScraper,
        json_output_path="raw/drivers/f1_drivers_{year}.json",
        legacy_json_output_path="drivers/f1_drivers_{year}.json",
        csv_output_path="drivers/f1_drivers.csv",
    )

    executor = LayerZeroExecutor(
        list_job_registry=(job,),
        validate_list_registry=lambda _registry: None,
        run_config_factory_map_builder=dict,
        default_config_factory=type(
            "_DefaultFactory",
            (),
            {"create_scraper_kwargs": lambda self, _job: {}},
        )(),
        run_and_export_function=lambda *args, **kwargs: None,
        merge_service=type("_MergeService", (), {"merge": lambda self, base_wiki_dir: None})(),
        job_hook=NullLayerZeroJobHook(),
        step_reporter=reporter,
        year_provider=lambda: 2026,
    )

    executor.run(
        RunConfig(output_dir=Path("/tmp"), include_urls=False, debug_dir=Path("/tmp/debug")),
        Path("/tmp/wiki"),
    )

    assert reporter.events == [
        {
            "phase": "start",
            "layer": "layer_zero",
            "step_type": "list_job",
            "step_name": "_FakeListScraper",
        },
        {
            "phase": "finish",
            "layer": "layer_zero",
            "step_type": "list_job",
            "step_name": "_FakeListScraper",
        },
    ]

