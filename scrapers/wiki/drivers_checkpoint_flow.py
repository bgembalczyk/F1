from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from collections.abc import Callable

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.orchestration import StepDeclaration
from scrapers.base.orchestration import StepOrchestrator
from scrapers.drivers.single_scraper import SingleDriverScraper

PARSER_VERSION = "drivers-checkpoint-flow-v1"


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
            driver_field = row.get("driver")
            if not isinstance(driver_field, dict):
                continue
            url = driver_field.get("url")
            text = driver_field.get("text")
            if not isinstance(url, str) or not url or url in seen_urls:
                continue
            if not isinstance(text, str):
                text = ""
            extracted.append({"name": text, "url": url})
            seen_urls.add(url)

        return extracted

    def _parse_layer1_details(
        self,
        checkpoint_records: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        checkpoint_urls = [record.get("url") for record in checkpoint_records]
        urls = [url for url in checkpoint_urls if isinstance(url, str) and url]

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
    flow = DriversCheckpointFlow(
        source_file=base_dir / "wiki" / "drivers" / "f1_drivers.json",
        checkpoint_file=base_dir / "checkpoints" / "step_0_layer0_drivers.json",
        layer1_output_file=base_dir / "checkpoints" / "step_1_layer1_drivers.json",
        registry_file=base_dir / "checkpoints" / "step_registry.json",
    )
    flow.run()
