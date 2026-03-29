from pathlib import Path

import pytest

from layers.orchestration.runners.grand_prix import GrandPrixRunner
from layers.seed.registry.entries import SeedRegistryEntry
from scrapers.base.run_config import RunConfig
from scrapers.base.runner import ScraperRunner
from scrapers.grands_prix.complete_scraper import F1CompleteGrandPrixDataExtractor


@pytest.mark.unit
def test_grand_prix_runner_uses_scraper_runner_path() -> None:
    calls: list[dict[str, object]] = []
    original_method = ScraperRunner.run_and_export

    def _capture_call(self, scraper_cls, json_rel, csv_rel=None) -> None:
        calls.append(
            {
                "scraper_cls": scraper_cls,
                "json_rel": json_rel,
                "csv_rel": csv_rel,
                "run_config": self._run_config,
            },
        )

    ScraperRunner.run_and_export = _capture_call

    try:
        runner = GrandPrixRunner()
        seed = SeedRegistryEntry(
            seed_name="grands_prix",
            wikipedia_url="https://example.com",
            output_category="grands_prix",
            list_scraper_cls=F1CompleteGrandPrixDataExtractor,
            default_output_path="raw/grands_prix/grands_prix.json",
            legacy_output_path="grands_prix/grands_prix.json",
        )
        run_config = RunConfig(output_dir=Path("/tmp"), include_urls=True)

        runner.run(seed, run_config, Path("/tmp/wiki"))
    finally:
        ScraperRunner.run_and_export = original_method

    assert calls == [
        {
            "scraper_cls": F1CompleteGrandPrixDataExtractor,
            "json_rel": "raw/grands_prix/grands_prix.json",
            "csv_rel": None,
            "run_config": run_config,
        },
    ]
