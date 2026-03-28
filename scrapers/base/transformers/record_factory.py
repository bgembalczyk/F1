from collections.abc import Callable
from typing import Any

from scrapers.base.factory.record_factory import RecordFactory
from scrapers.base.logging import get_logger
from scrapers.base.normalization import EmptyValuePolicy
from scrapers.base.transformers.record_transformer import RecordTransformer
from validation.validator_base import ExportRecord

FACTORY_FALLBACK_EXCEPTIONS = (TypeError, ValueError, KeyError, AttributeError)


class RecordFactoryTransformer(RecordTransformer):
    def __init__(
        self,
        record_factory: RecordFactory | Callable[[dict[str, Any]], Any] | type,
        *,
        fallback_on_error: bool = False,
        empty_value_policy: EmptyValuePolicy = EmptyValuePolicy.NORMALIZE,
    ) -> None:
        super().__init__(empty_value_policy=empty_value_policy)
        self.record_factory = record_factory
        self.fallback_on_error = fallback_on_error
        self.logger = get_logger(self.__class__.__name__)

    def _apply_factory(self, record: ExportRecord) -> ExportRecord | Any:
        if hasattr(self.record_factory, "create"):
            return self.record_factory.create(record)
        if isinstance(self.record_factory, type):
            return self.record_factory(**record)
        return self.record_factory(record)

    def _apply_factory_with_fallback(self, record: ExportRecord) -> ExportRecord | Any:
        try:
            normalized = self.normalize_record(record)
            return self._apply_factory(normalized)
        except FACTORY_FALLBACK_EXCEPTIONS:
            self.logger.warning(
                "record_factory failed, falling back to raw record",
                exc_info=True,
            )
            return record

    def transform(self, records: list[ExportRecord]) -> list[ExportRecord]:
        transformed: list[ExportRecord] = []
        if not self.fallback_on_error:
            for record in records:
                normalized = self.normalize_record(record)
                transformed.append(self._apply_factory(normalized))
            return transformed

        transformed.extend(
            self._apply_factory_with_fallback(record) for record in records
        )
        return transformed
