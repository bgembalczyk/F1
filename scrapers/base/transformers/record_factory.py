from collections.abc import Callable
from typing import Any

from scrapers.base.logging import get_logger
from scrapers.base.normalization import EmptyValuePolicy
from scrapers.base.transformers.record_transformer import RecordTransformer
from validation.validator_base import ExportRecord


class RecordFactoryTransformer(RecordTransformer):
    def __init__(
        self,
        record_factory: Callable[[dict[str, Any]], Any] | type,
        *,
        fallback_on_error: bool = False,
        empty_value_policy: EmptyValuePolicy = EmptyValuePolicy.NORMALIZE,
    ) -> None:
        super().__init__(empty_value_policy=empty_value_policy)
        self.record_factory = record_factory
        self.fallback_on_error = fallback_on_error
        self.logger = get_logger(self.__class__.__name__)

    def _apply_factory(self, record: ExportRecord) -> ExportRecord | Any:
        if isinstance(self.record_factory, type):
            return self.record_factory(**record)
        return self.record_factory(record)

    def transform(self, records: list[ExportRecord]) -> list[ExportRecord]:
        transformed: list[ExportRecord] = []
        for record in records:
            try:
                normalized = self.normalize_record(record)
                transformed.append(self._apply_factory(normalized))
            except Exception:
                if not self.fallback_on_error:
                    raise
                self.logger.warning(
                    "record_factory failed, falling back to raw record",
                    exc_info=True,
                )
                transformed.append(record)
        return transformed
