from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

from layers.checkpoints.helpers import _extract_driver_seed_row
from layers.checkpoints.helpers import _filter_checkpoint_urls
from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.orchestration.step_orchestrator import StepDeclaration
from scrapers.base.orchestration.step_orchestrator import StepOrchestrator
from scrapers.data_paths import default_data_paths
from scrapers.drivers.single_scraper import SingleDriverScraper
from scrapers.wiki.contants import PARSER_VERSION

if TYPE_CHECKING:
    from collections.abc import Callable



class DriversCheckpointFlow:
    def __init__(
        self,
        *,
        source_file: Path,
        checkpoint_file: Path,
        layer1_output_file: Path,
        registry_file: Path,
        source_category: str = "drivers",
        parser_version: str = PARSER_VERSION,
        detail_fetcher: Callable[[str], dict[str, Any]] | None = None,
    ) -> None:
        self.source_file = source_file
        self.source_category = source_category
        self.checkpoint_file = checkpoint_file
        self.layer1_output_file = layer1_output_file
        self.registry_file = registry_file
        self.parser_version = parser_version
        self.detail_fetcher = detail_fetcher or self._fetch_driver_details

        self._base_dir = self._resolve_base_data_dir()
        self.orchestrator = StepOrchestrator(base_dir=self._base_dir)

    def run(self) -> None:
        self.run_layer0_checkpoint()
        self.run_layer1_from_checkpoint()

    def run_layer0_checkpoint(self) -> None:
        step = StepDeclaration(
            step_id=0,
            layer="layer0",
            input_source=str(self.source_file),
            parser=self._parse_layer0_urls,
            output_target="checkpoints",
        )
        result = self.orchestrator.run(step, self.source_category)
        if Path(result.output_path) != self.checkpoint_file:
            self._copy_file(Path(result.output_path), self.checkpoint_file)

    def run_layer1_from_checkpoint(self) -> None:
        checkpoint_input = self.checkpoint_file.stem
        step = StepDeclaration(
            step_id=1,
            layer="layer1",
            input_source=checkpoint_input,
            parser=self._parse_layer1_details,
            output_target="checkpoints",
        )
        result = self.orchestrator.run(step, self.source_category)
        if Path(result.output_path) != self.layer1_output_file:
            self._copy_file(Path(result.output_path), self.layer1_output_file)

    def _parse_layer0_urls(
        self,
        source_data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        extracted: list[dict[str, Any]] = []
        seen_urls: set[str] = set()

        for row in source_data:
            extracted_row = _extract_driver_seed_row(row)
            if extracted_row is None:
                continue
            name, url = extracted_row
            if url in seen_urls:
                continue
            extracted.append({"name": name, "url": url})
            seen_urls.add(url)

        return extracted

    def _parse_layer1_details(
        self,
        checkpoint_records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        urls = _filter_checkpoint_urls(checkpoint_records)

        existing = self._load_existing_layer1_records()
        processed_urls = {
            record.get("url") for record in existing if isinstance(record, dict)
        }

        new_records = []
        for url in urls:
            if url in processed_urls:
                continue
            details = self.detail_fetcher(url)
            new_records.append(details)

        return existing + new_records

    def _load_existing_layer1_records(self) -> list[dict[str, Any]]:
        if not self.layer1_output_file.exists():
            return []
        payload = self._load_json(self.layer1_output_file)
        if isinstance(payload, dict):
            records = payload.get("records", [])
            if isinstance(records, list):
                return [record for record in records if isinstance(record, dict)]
            return []
        if not isinstance(payload, list):
            return []
        return [record for record in payload if isinstance(record, dict)]

    @staticmethod
    def _load_json(path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _copy_file(source: Path, target: Path) -> None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

    def _resolve_base_data_dir(self) -> Path:
        if self.source_file.parts:
            try:
                index = self.source_file.parts.index("data")
                return Path(*self.source_file.parts[: index + 1])
            except ValueError:
                pass
        return Path("data")

    @staticmethod
    def _fetch_driver_details(url: str) -> dict[str, Any]:
        options = init_scraper_options(None, include_urls=True)
        scraper = SingleDriverScraper(options=options)
        records = scraper.fetch_by_url(url)
        if records:
            return records[0]
        return {"url": url, "details": None}


def run_drivers_checkpoint_first_flow(
    *,
    base_dir: Path = Path("data"),
) -> None:
    paths = default_data_paths(base_dir=base_dir)
    source_file = paths.resolve_compatible_input("drivers", "f1_drivers.json")
    if source_file is None:
        source_file = paths.raw_file("drivers", "f1_drivers.json")

    flow = DriversCheckpointFlow(
        source_file=source_file,
        checkpoint_file=paths.checkpoint_file("step_0_layer0_drivers.json"),
        layer1_output_file=paths.checkpoint_file("step_1_layer1_drivers.json"),
        registry_file=paths.checkpoint_file("step_registry.json"),
    )
    flow.run()
