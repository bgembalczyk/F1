from __future__ import annotations

from logging import getLogger
from typing import TYPE_CHECKING

from scrapers.base.pipeline_runner import ScraperPipelineRunner

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


def test_pipeline_runner_executes_steps_iteratively_and_reports_quality() -> None:
    quality_calls: list[tuple[str, list[dict[str, object]]]] = []

    seen_inputs: dict[str, object] = {}

    def parse_records(soup: BeautifulSoup) -> list[dict[str, object]]:
        seen_inputs["parse"] = soup.title
        return [{"value": 1}]

    def normalize_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
        seen_inputs["normalize"] = records
        return [{"value": records[0]["value"], "normalized": True}]

    def transform_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
        seen_inputs["transform"] = records
        return [{"value": records[0]["value"], "transformed": True}]

    def validate_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
        seen_inputs["validate"] = records
        return [{"value": records[0]["value"], "validated": True}]

    def post_process_records(
        records: list[dict[str, object]],
    ) -> list[dict[str, object]]:
        seen_inputs["post_process"] = records
        return [{"value": records[0]["value"], "done": True}]

    runner = ScraperPipelineRunner(
        logger=getLogger(__name__),
        write_step_quality_report=lambda step_name, records: quality_calls.append(
            (step_name, records),
        ),
        parse_records=parse_records,
        normalize_records=normalize_records,
        transform_records=transform_records,
        validate_records=validate_records,
        post_process_records=post_process_records,
    )

    result = runner.run(
        run_id="run-123",
        html="<html><head><title>ok</title></head></html>",
    )

    assert result == [{"value": 1, "done": True}]
    assert seen_inputs["normalize"] == [{"value": 1}]
    assert seen_inputs["transform"] == [{"value": 1, "normalized": True}]
    assert seen_inputs["validate"] == [{"value": 1, "transformed": True}]
    assert seen_inputs["post_process"] == [{"value": 1, "validated": True}]

    assert [step_name for step_name, _ in quality_calls] == [
        "parse",
        "normalize",
        "transform",
        "validate",
        "post_process",
    ]
