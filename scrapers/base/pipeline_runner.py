from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import asdict
from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import TypeAlias
from typing import cast

from scrapers.base.records import NormalizedRecord
from scrapers.base.records import RawRecord

if TYPE_CHECKING:
    from logging import Logger

from bs4 import BeautifulSoup

from models.mappers.serialization import to_dict_list
from scrapers.base.errors import normalize_pipeline_error
from validation.validator_base import ExportRecord

PipelineResult: TypeAlias = (
    list[ExportRecord] | list[RawRecord] | list[NormalizedRecord]
)
StepRunner: TypeAlias = Callable[[], PipelineResult]
StepQualityWriter: TypeAlias = Callable[[str, list[dict[str, object]]], None]
ErrorSummaryWriter: TypeAlias = Callable[[dict[str, object]], None]
PipelineInput: TypeAlias = BeautifulSoup | PipelineResult

ERROR_FIX_LINKS: dict[str, str] = {
    "pipeline.parse_failed": "docs/ERROR_FIX_GUIDE.md#pipelineparse_failed",
    "pipeline.normalize_failed": "docs/ERROR_FIX_GUIDE.md#pipelinenormalize_failed",
    "pipeline.transform_failed": "docs/ERROR_FIX_GUIDE.md#pipelinetransform_failed",
    "pipeline.validate_failed": "docs/ERROR_FIX_GUIDE.md#pipelinevalidate_failed",
    "pipeline.post_process_failed": "docs/ERROR_FIX_GUIDE.md#pipelinepost_process_failed",
}


@dataclass(frozen=True)
class PipelineIssue:
    code: str
    level: str
    domain: str
    source: str
    record: str | None
    suggestion: str | None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PipelineStep:
    step_name: str
    run_step: Callable[[PipelineInput], PipelineResult]
    to_dict: bool = False


class ScraperPipelineRunner:
    def __init__(
        self,
        *,
        logger: Logger,
        write_step_quality_report: StepQualityWriter,
        write_error_summary_report: ErrorSummaryWriter | None = None,
        parse_records: Callable[[BeautifulSoup], list[RawRecord]],
        normalize_records: Callable[[list[RawRecord]], list[NormalizedRecord]],
        transform_records: Callable[[list[NormalizedRecord]], list[ExportRecord]],
        validate_records: Callable[[list[ExportRecord]], list[ExportRecord]],
        post_process_records: Callable[[list[ExportRecord]], list[ExportRecord]],
    ) -> None:
        self.logger = logger
        self._write_step_quality_report = write_step_quality_report
        self._write_error_summary_report = write_error_summary_report
        self._parse_records = parse_records
        self._normalize_records = normalize_records
        self._transform_records = transform_records
        self._validate_records = validate_records
        self._post_process_records = post_process_records

    def run(self, *, run_id: str, html: str) -> list[ExportRecord]:
        soup = BeautifulSoup(html, "html.parser")
        issues: list[PipelineIssue] = []
        steps = [
            PipelineStep(
                step_name="parse",
                run_step=self._parse_step,
            ),
            PipelineStep(
                step_name="normalize",
                run_step=self._normalize_step,
                to_dict=True,
            ),
            PipelineStep(
                step_name="transform",
                run_step=self._transform_step,
                to_dict=True,
            ),
            PipelineStep(
                step_name="validate",
                run_step=self._validate_step,
                to_dict=True,
            ),
            PipelineStep(
                step_name="post_process",
                run_step=self._post_process_step,
                to_dict=True,
            ),
        ]

        records: PipelineInput = soup
        try:
            for step in steps:
                records = self._log_step(
                    run_id,
                    step.step_name,
                    lambda step_runner=step.run_step, step_input=records: step_runner(
                        step_input,
                    ),
                    to_dict=step.to_dict,
                    issues=issues,
                )
        finally:
            self._write_error_summary(run_id=run_id, issues=issues)

        return list(records)

    def _parse_step(self, step_input: PipelineInput) -> PipelineResult:
        if not isinstance(step_input, BeautifulSoup):
            msg = "parse step expects BeautifulSoup input"
            raise TypeError(msg)
        return self._parse_records(step_input)

    def _normalize_step(self, step_input: PipelineInput) -> PipelineResult:
        if isinstance(step_input, BeautifulSoup):
            msg = "normalize step expects raw records input"
            raise TypeError(msg)
        return self._normalize_records(cast("list[RawRecord]", list(step_input)))

    def _transform_step(self, step_input: PipelineInput) -> PipelineResult:
        if isinstance(step_input, BeautifulSoup):
            msg = "transform step expects normalized records input"
            raise TypeError(msg)
        return self._transform_records(cast("list[NormalizedRecord]", step_input))

    def _validate_step(self, step_input: PipelineInput) -> PipelineResult:
        if isinstance(step_input, BeautifulSoup):
            msg = "validate step expects export records input"
            raise TypeError(msg)
        return self._validate_records(cast("list[ExportRecord]", step_input))

    def _post_process_step(self, step_input: PipelineInput) -> PipelineResult:
        if isinstance(step_input, BeautifulSoup):
            msg = "post_process step expects export records input"
            raise TypeError(msg)
        return self._post_process_records(cast("list[ExportRecord]", step_input))

    def _log_step(
        self,
        run_id: str,
        step_name: str,
        run_step: StepRunner,
        *,
        to_dict: bool = False,
        issues: list[PipelineIssue],
    ) -> PipelineResult:
        step_label = step_name.replace("_", "-")
        self.logger.debug("Scrape run %s: start %s", run_id, step_label)
        try:
            records = run_step()
        except Exception as exc:
            normalized = normalize_pipeline_error(
                exc,
                code=f"pipeline.{step_name}_failed",
                message=f"Pipeline step '{step_name}' failed.",
                domain=step_name,
                source_name=step_name,
            )
            issues.append(
                PipelineIssue(
                    code=normalized.code,
                    level=normalized.level,
                    domain=normalized.domain,
                    source=normalized.source_name or step_name,
                    record=normalized.record,
                    suggestion=normalized.suggestion,
                ),
            )
            raise normalized from exc
        self.logger.debug("Scrape run %s: finish %s", run_id, step_label)
        self._write_step_quality_report(
            step_name,
            to_dict_list(list(records)) if to_dict else list(records),
        )
        return records

    def _write_error_summary(self, *, run_id: str, issues: list[PipelineIssue]) -> None:
        if self._write_error_summary_report is None:
            return
        by_code = Counter(issue.code for issue in issues)
        top_codes = [code for code, _ in by_code.most_common(5)]
        payload: dict[str, object] = {
            "run_id": run_id,
            "total_errors": len(issues),
            "errors": [issue.as_dict() for issue in issues],
            "aggregation_by_code": dict(by_code),
            "how_to_fix_links": {
                code: ERROR_FIX_LINKS[code]
                for code in top_codes
                if code in ERROR_FIX_LINKS
            },
        }
        self._write_error_summary_report(payload)
