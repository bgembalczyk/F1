from __future__ import annotations

from dataclasses import dataclass
from typing import get_type_hints

from models.mappers.serialization import QualityRecord
from scrapers.base.pipeline_runner import ScraperPipelineRunner
from scrapers.base.scraper_components import PipelineOrchestrator
from scrapers.base.scraper_components import QualityReportService


class _LoggerStub:
    def debug(self, *_args, **_kwargs) -> None:
        return None


@dataclass
class _RawDataclassRecord:
    name: str


def test_quality_writer_signatures_use_shared_quality_record_alias() -> None:
    service_hints = get_type_hints(QualityReportService.write_step)
    orchestrator_hints = get_type_hints(PipelineOrchestrator._write_pipeline_quality_report)

    assert service_hints["records"] == list[QualityRecord]
    assert orchestrator_hints["records"] == list[QualityRecord]


def test_pipeline_runner_serializes_all_step_payloads_for_quality_writer() -> None:
    calls: list[tuple[str, list[QualityRecord]]] = []

    def writer(step_name: str, records: list[QualityRecord]) -> None:
        calls.append((step_name, records))

    runner = ScraperPipelineRunner(
        logger=_LoggerStub(),
        write_step_quality_report=writer,
        parse_records=lambda _soup: [_RawDataclassRecord(name="alpha")],
        normalize_records=lambda records: [{"name": records[0].name}],
        transform_records=lambda records: [{"name": records[0]["name"], "ok": True}],
        validate_records=lambda records: records,
        post_process_records=lambda records: records,
    )

    runner.run(run_id="test-run", html="<html></html>")

    assert [step for step, _ in calls] == [
        "parse",
        "normalize",
        "transform",
        "validate",
        "post_process",
    ]
    assert calls[0][1] == [{"name": "alpha"}]
    assert all(isinstance(step_records[0], dict) for _, step_records in calls)
