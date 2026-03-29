from __future__ import annotations

from collections.abc import Callable
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
from validation.validator_base import ExportRecord

PipelineResult: TypeAlias = (
    list[ExportRecord] | list[RawRecord] | list[NormalizedRecord]
)
StepRunner: TypeAlias = Callable[[], PipelineResult]
StepQualityWriter: TypeAlias = Callable[[str, list[dict[str, object]]], None]
PipelineInput: TypeAlias = BeautifulSoup | PipelineResult


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
        parse_records: Callable[[BeautifulSoup], list[RawRecord]],
        normalize_records: Callable[[list[RawRecord]], list[NormalizedRecord]],
        transform_records: Callable[[list[NormalizedRecord]], list[ExportRecord]],
        validate_records: Callable[[list[ExportRecord]], list[ExportRecord]],
        post_process_records: Callable[[list[ExportRecord]], list[ExportRecord]],
    ) -> None:
        self.logger = logger
        self._write_step_quality_report = write_step_quality_report
        self._parse_records = parse_records
        self._normalize_records = normalize_records
        self._transform_records = transform_records
        self._validate_records = validate_records
        self._post_process_records = post_process_records

    def run(self, *, run_id: str, html: str) -> list[ExportRecord]:
        soup = BeautifulSoup(html, "html.parser")
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
        for step in steps:
            records = self._log_step(
                run_id,
                step.step_name,
                lambda step_runner=step.run_step, step_input=records: step_runner(
                    step_input,
                ),
                to_dict=step.to_dict,
            )

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
    ) -> PipelineResult:
        step_label = step_name.replace("_", "-")
        self.logger.debug("Scrape run %s: start %s", run_id, step_label)
        records = run_step()
        self.logger.debug("Scrape run %s: finish %s", run_id, step_label)
        self._write_step_quality_report(
            step_name,
            to_dict_list(list(records)) if to_dict else list(records),
        )
        return records
