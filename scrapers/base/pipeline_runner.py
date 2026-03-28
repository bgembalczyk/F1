from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING
from typing import TypeAlias

if TYPE_CHECKING:
    from logging import Logger

from bs4 import BeautifulSoup

from models.mappers.serialization import to_dict_list
from scrapers.base.records import NormalizedRecord
from scrapers.base.records import RawRecord
from validation.validator_base import ExportRecord

PipelineResult: TypeAlias = (
    list[ExportRecord] | list[RawRecord] | list[NormalizedRecord]
)
StepRunner: TypeAlias = Callable[[], PipelineResult]
StepQualityWriter: TypeAlias = Callable[[str, list[dict[str, object]]], None]


class ScraperPipelineRunner:
    def __init__(
        self,
        *,
        logger: Logger,
        write_step_quality_report: StepQualityWriter,
        parse_records: Callable[[BeautifulSoup], list[RawRecord]],
        normalize_records: Callable[[list[RawRecord]], list[NormalizedRecord]],
        pre_validate_transform_records: Callable[
            [list[NormalizedRecord]],
            list[ExportRecord],
        ],
        enrich_records: Callable[[list[ExportRecord]], list[ExportRecord]],
        validate_records: Callable[[list[ExportRecord]], list[ExportRecord]],
        post_validate_transform_records: Callable[
            [list[ExportRecord]],
            list[ExportRecord],
        ],
        post_process_records: Callable[[list[ExportRecord]], list[ExportRecord]],
    ) -> None:
        self.logger = logger
        self._write_step_quality_report = write_step_quality_report
        self._parse_records = parse_records
        self._normalize_records = normalize_records
        self._pre_validate_transform_records = pre_validate_transform_records
        self._enrich_records = enrich_records
        self._validate_records = validate_records
        self._post_validate_transform_records = post_validate_transform_records
        self._post_process_records = post_process_records

    def run(self, *, run_id: str, html: str) -> list[ExportRecord]:
        soup = BeautifulSoup(html, "html.parser")
        raw_records = self._log_step(run_id, "parse", lambda: self._parse_records(soup))
        normalized_records = self._log_step(
            run_id,
            "normalize",
            lambda: self._normalize_records(list(raw_records)),
            to_dict=True,
        )
        pre_validated_records = self._log_step(
            run_id,
            "transform_pre_validate",
            lambda: self._pre_validate_transform_records(normalized_records),
            to_dict=True,
        )
        enriched_records = self._log_step(
            run_id,
            "transform_enrich",
            lambda: self._enrich_records(pre_validated_records),
            to_dict=True,
        )
        validated_records = self._log_step(
            run_id,
            "validate",
            lambda: self._validate_records(enriched_records),
            to_dict=True,
        )
        post_validated_records = self._log_step(
            run_id,
            "transform_post_validate",
            lambda: self._post_validate_transform_records(validated_records),
            to_dict=True,
        )
        return self._log_step(
            run_id,
            "post_process",
            lambda: self._post_process_records(post_validated_records),
            to_dict=True,
        )

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
