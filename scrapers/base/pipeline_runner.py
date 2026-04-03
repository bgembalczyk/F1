from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import warnings
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
    """Uruchamia workflow etapów parsowania rekordu scrapera.

    Wejście: funkcje kroków pipeline i logger.
    Wyjście: lista rekordów po pełnym workflow.
    """

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
        """Run workflow parse->normalize->transform->validate->post_process.

        Wejście: run_id oraz surowy HTML strony.
        Wyjście: lista rekordów eksportowych po pipeline.
        """
        soup = BeautifulSoup(html, "html.parser")
        steps = [
            PipelineStep(
                step_name="parse",
                run_step=self._execute_parse_step,
            ),
            PipelineStep(
                step_name="normalize",
                run_step=self._execute_normalize_step,
                to_dict=True,
            ),
            PipelineStep(
                step_name="transform",
                run_step=self._execute_transform_step,
                to_dict=True,
            ),
            PipelineStep(
                step_name="validate",
                run_step=self._execute_validate_step,
                to_dict=True,
            ),
            PipelineStep(
                step_name="post_process",
                run_step=self._execute_post_process_step,
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

    def _execute_parse_step(self, step_input: PipelineInput) -> PipelineResult:
        """Execute techniczny krok parsowania BeautifulSoup -> RawRecord.

        Wejście: BeautifulSoup jako wejście pipeline.
        Wyjście: lista rekordów raw.
        """
        if not isinstance(step_input, BeautifulSoup):
            msg = "parse step expects BeautifulSoup input"
            raise TypeError(msg)
        return self._parse_records(step_input)

    def _execute_normalize_step(self, step_input: PipelineInput) -> PipelineResult:
        """Execute techniczny krok normalizacji raw -> normalized.

        Wejście: lista rekordów raw.
        Wyjście: lista rekordów znormalizowanych.
        """
        if isinstance(step_input, BeautifulSoup):
            msg = "normalize step expects raw records input"
            raise TypeError(msg)
        return self._normalize_records(cast("list[RawRecord]", list(step_input)))

    def _execute_transform_step(self, step_input: PipelineInput) -> PipelineResult:
        """Execute techniczny krok transformacji normalized -> export.

        Wejście: lista rekordów znormalizowanych.
        Wyjście: lista rekordów eksportowych.
        """
        if isinstance(step_input, BeautifulSoup):
            msg = "transform step expects normalized records input"
            raise TypeError(msg)
        return self._transform_records(cast("list[NormalizedRecord]", step_input))

    def _execute_validate_step(self, step_input: PipelineInput) -> PipelineResult:
        """Execute techniczny krok walidacji rekordów eksportowych.

        Wejście: lista rekordów eksportowych.
        Wyjście: zwalidowana lista rekordów eksportowych.
        """
        if isinstance(step_input, BeautifulSoup):
            msg = "validate step expects export records input"
            raise TypeError(msg)
        return self._validate_records(cast("list[ExportRecord]", step_input))

    def _execute_post_process_step(self, step_input: PipelineInput) -> PipelineResult:
        """Execute techniczny krok post-processingu rekordów.

        Wejście: lista rekordów eksportowych.
        Wyjście: lista rekordów po post-processingu.
        """
        if isinstance(step_input, BeautifulSoup):
            msg = "post_process step expects export records input"
            raise TypeError(msg)
        return self._post_process_records(cast("list[ExportRecord]", step_input))

    def _parse_step(self, step_input: PipelineInput) -> PipelineResult:
        """Deprecated alias for `_execute_parse_step`."""
        warnings.warn(
            "`_parse_step` is deprecated; use `_execute_parse_step`.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._execute_parse_step(step_input)

    def _normalize_step(self, step_input: PipelineInput) -> PipelineResult:
        """Deprecated alias for `_execute_normalize_step`."""
        warnings.warn(
            "`_normalize_step` is deprecated; use `_execute_normalize_step`.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._execute_normalize_step(step_input)

    def _transform_step(self, step_input: PipelineInput) -> PipelineResult:
        """Deprecated alias for `_execute_transform_step`."""
        warnings.warn(
            "`_transform_step` is deprecated; use `_execute_transform_step`.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._execute_transform_step(step_input)

    def _validate_step(self, step_input: PipelineInput) -> PipelineResult:
        """Deprecated alias for `_execute_validate_step`."""
        warnings.warn(
            "`_validate_step` is deprecated; use `_execute_validate_step`.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._execute_validate_step(step_input)

    def _post_process_step(self, step_input: PipelineInput) -> PipelineResult:
        """Deprecated alias for `_execute_post_process_step`."""
        warnings.warn(
            "`_post_process_step` is deprecated; use `_execute_post_process_step`.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._execute_post_process_step(step_input)

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
