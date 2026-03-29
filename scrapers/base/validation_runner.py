from __future__ import annotations

from typing import TYPE_CHECKING

from scrapers.base.errors import ScraperValidationError

if TYPE_CHECKING:
    from collections.abc import Callable
    from logging import Logger

    from validation.validator_base import ExportRecord
    from validation.validator_base import RecordValidator


class ValidationRunner:
    def __init__(
        self,
        *,
        validator: RecordValidator,
        validation_mode: str,
        logger: Logger,
        write_quality_report: Callable[[], None],
        url: str | None,
    ) -> None:
        self.validator = validator
        self.validation_mode = validation_mode
        self.logger = logger
        self._write_quality_report = write_quality_report
        self.url = url

    def validate(self, records: list[ExportRecord]) -> list[ExportRecord]:
        self.validator.reset_stats()
        valid_records: list[ExportRecord] = []
        for index, record in enumerate(records):
            if self._process_record(index, record, valid_records):
                continue
        self._log_validation_summary(total=len(records), valid=len(valid_records))
        self._write_quality_report()
        return valid_records

    def _process_record(
        self,
        index: int,
        record: ExportRecord,
        valid_records: list[ExportRecord],
    ) -> bool:
        errors_for_tracking, messages = self._collect_validation_errors(record)
        self.validator.record_validation_result(errors_for_tracking)
        if not errors_for_tracking:
            valid_records.append(record)
            return True

        message = self._validation_error_message(index, errors_for_tracking, messages)
        if self.validation_mode == "soft":
            self.logger.warning(message)
            return True

        self._write_quality_report()
        raise ScraperValidationError(message=message, url=self.url)

    def _collect_validation_errors(self, record: ExportRecord):
        errors = self.validator.validate(record)
        record_factory_errors = self.validator.validate_record_factory(record)
        errors_for_tracking = list(errors)
        messages = [error.message for error in errors]
        if not record_factory_errors:
            return errors_for_tracking, messages

        errors_for_tracking.extend(record_factory_errors)
        record_factory_label = self._record_factory_label(default="record_factory")
        messages.extend(
            [
                f"{record_factory_label}: {error.message}"
                for error in record_factory_errors
            ],
        )
        return errors_for_tracking, messages

    def _record_factory_label(self, *, default: str | None = None) -> str | None:
        validator = self.validator.record_factory_validator
        if validator is None:
            return default
        return validator.__class__.__name__

    def _validation_error_message(
        self,
        index: int,
        errors_for_tracking: list,
        messages: list[str],
    ) -> str:
        model_label = self._record_factory_label()
        return (
            f"Validation failed for record #{index}"
            f"{f' ({model_label})' if model_label else ''} "
            f"with {len(errors_for_tracking)} error(s): {', '.join(messages)}"
        )

    def _log_validation_summary(self, *, total: int, valid: int) -> None:
        rejected = total - valid
        if not rejected:
            return
        self.logger.info(
            "Validation rejected %d record(s) out of %d",
            rejected,
            total,
        )
        self.logger.info("Validation filtered records: %d -> %d", total, valid)
