from __future__ import annotations

from pathlib import Path
from typing import Any

from scrapers.base.helpers.http import init_scraper_options
from scrapers.base.orchestration import StepDeclaration
from scrapers.base.orchestration import StepOrchestrator
from scrapers.constructors.single_scraper import SingleConstructorScraper
from scrapers.drivers.single_scraper import SingleDriverScraper

from collections.abc import Callable
from collections.abc import Iterable

DetailFetcher = Callable[[str], dict[str, Any]]


class SeedSectionOrchestrationFlow:
    """L0 seed -> L1 wiki sections for selected domains."""

    def __init__(
        self,
        *,
        base_dir: Path = Path("data"),
        detail_fetchers: dict[str, DetailFetcher] | None = None,
    ) -> None:
        self.base_dir = base_dir
        self.orchestrator = StepOrchestrator(base_dir=base_dir)
        self.detail_fetchers = detail_fetchers or {}

    def run(self, domains: Iterable[str] = ("drivers", "constructors")) -> dict[str, str]:
        outputs: dict[str, str] = {}
        for domain in domains:
            self._run_domain(domain)
            outputs[domain] = str(self._checkpoint_file(f"step_1_layer1_{domain}.json"))

        report_path = self.orchestrator.audit_trail.write_regression_report(
            self._checkpoint_file("step_regression_report.md"),
        )
        outputs["report"] = str(report_path)
        return outputs

    def _checkpoint_file(self, filename: str) -> Path:
        return self.base_dir / "checkpoints" / filename

    def _run_domain(self, domain: str) -> None:
        step0 = StepDeclaration(
            step_id=0,
            layer="layer0",
            input_source=domain,
            parser=lambda rows, item_key=domain[:-1]: self._parse_seed_urls(rows, item_key),
            output_target="checkpoints",
        )
        self.orchestrator.run(step0, domain)

        step1 = StepDeclaration(
            step_id=1,
            layer="layer1",
            input_source=f"step_0_layer0_{domain}",
            parser=lambda rows, current_domain=domain: self._parse_sections(rows, current_domain),
            output_target="checkpoints",
        )
        self.orchestrator.run(step1, domain)

    @staticmethod
    def _parse_seed_urls(
        seed_rows: list[dict[str, Any]],
        item_key: str,
    ) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        for row in seed_rows:
            field = row.get(item_key)
            if not isinstance(field, dict):
                continue
            url = field.get("url")
            if not isinstance(url, str) or not url or url in seen_urls:
                continue
            text = field.get("text") if isinstance(field.get("text"), str) else ""
            records.append({"name": text, "url": url})
            seen_urls.add(url)
        return records

    def _parse_sections(
        self,
        seed_urls: list[dict[str, Any]],
        domain: str,
    ) -> list[dict[str, Any]]:
        fetcher = self.detail_fetchers.get(domain) or self._default_fetcher(domain)
        output: list[dict[str, Any]] = []
        for record in seed_urls:
            url = record.get("url")
            if not isinstance(url, str) or not url:
                continue
            output.append(fetcher(url))
        return output

    @staticmethod
    def _default_fetcher(domain: str) -> DetailFetcher:
        options = init_scraper_options(None, include_urls=True)
        if domain == "drivers":
            scraper = SingleDriverScraper(options=options)
            return lambda url: _pick_first(scraper.fetch_by_url(url), url)
        if domain == "constructors":
            scraper = SingleConstructorScraper(options=options)
            return lambda url: _pick_first(scraper.fetch_by_url(url), url)

        msg = f"Unsupported domain for section flow: {domain}"
        raise ValueError(msg)


def _pick_first(records: list[dict[str, Any]], url: str) -> dict[str, Any]:
    if records:
        return records[0]
    return {"url": url, "details": None}


def run_seed_section_orchestration(*, base_dir: Path = Path("data")) -> dict[str, str]:
    flow = SeedSectionOrchestrationFlow(base_dir=base_dir)
    return flow.run()
