from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from collections.abc import Callable

from scrapers.base.helpers.http import init_scraper_options
from scrapers.data_paths import default_data_paths
from scrapers.drivers.single_scraper import SingleDriverScraper

PARSER_VERSION = "drivers-checkpoint-flow-v1"


@dataclass(frozen=True)
class StepRun:
    step: str
    input: str
    parser: str
    output: str


class StepRegistry:
    def __init__(self, path: Path) -> None:
        self.path = path

    def record(self, run: StepRun) -> None:
        payload = self._load()
        steps = payload.get("steps", [])
        updated = [entry for entry in steps if entry.get("step") != run.step]
        updated.append(
            {
                "step": run.step,
                "input": run.input,
                "parser": run.parser,
                "output": run.output,
                "recorded_at": datetime.now(tz=timezone.utc).isoformat(),
            },
        )
        payload["steps"] = updated
        self.path.parent.mkdir(parents=True, exist_ok=True)
        body = json.dumps(payload, ensure_ascii=False, indent=2)
        self.path.write_text(body, encoding="utf-8")

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"steps": []}
        return json.loads(self.path.read_text(encoding="utf-8"))


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
        self.registry = StepRegistry(registry_file)
        self.parser_version = parser_version
        self.detail_fetcher = detail_fetcher or self._fetch_driver_details

    def run(self) -> None:
        self.run_layer0_checkpoint()
        self.run_layer1_from_checkpoint()

    def run_layer0_checkpoint(self) -> None:
        source_path = default_data_paths().resolve_legacy_wiki_read(self.source_file)
        source_data = self._load_json(source_path)
        urls = self._extract_driver_urls(source_data)

        checkpoint_payload = {
            "metadata": {
                "source_file": str(self.source_file),
                "source_category": self.source_category,
                "scraped_at": datetime.now(tz=timezone.utc).isoformat(),
                "parser_version": self.parser_version,
            },
            "records": urls,
        }

        self.checkpoint_file.parent.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file.write_text(
            json.dumps(checkpoint_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.registry.record(
            StepRun(
                step="step_0_layer0_drivers",
                input=str(source_path),
                parser=self.parser_version,
                output=str(self.checkpoint_file),
            ),
        )

    def run_layer1_from_checkpoint(self) -> None:
        checkpoint_payload = self._load_json(self.checkpoint_file)
        checkpoint_records = checkpoint_payload.get("records", [])
        checkpoint_urls = [
            record.get("url")
            for record in checkpoint_records
            if isinstance(record, dict)
        ]
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

        merged_records = existing + new_records

        self.layer1_output_file.parent.mkdir(parents=True, exist_ok=True)
        self.layer1_output_file.write_text(
            json.dumps(merged_records, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.registry.record(
            StepRun(
                step="step_1_layer1_drivers",
                input=str(self.checkpoint_file),
                parser=self.detail_fetcher.__name__,
                output=str(self.layer1_output_file),
            ),
        )

    def _load_existing_layer1_records(self) -> list[dict[str, Any]]:
        if not self.layer1_output_file.exists():
            return []
        payload = self._load_json(self.layer1_output_file)
        if not isinstance(payload, list):
            return []
        return [record for record in payload if isinstance(record, dict)]

    @staticmethod
    def _load_json(path: Path) -> Any:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _extract_driver_urls(source_data: Any) -> list[dict[str, str]]:
        if not isinstance(source_data, list):
            return []

        extracted: list[dict[str, str]] = []
        seen_urls: set[str] = set()

        for row in source_data:
            if not isinstance(row, dict):
                continue
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
        checkpoint_file=base_dir / "checkpoints" / "drivers" / "step_0_layer0_drivers.json",
        layer1_output_file=base_dir / "normalized" / "drivers" / "sections" / "step_1_layer1_drivers.json",
        registry_file=base_dir / "checkpoints" / "drivers" / "step_registry.json",
    )
    flow.run()
