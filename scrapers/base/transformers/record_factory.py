from typing import Any, Callable, Dict, List

from scrapers.base.logging import get_logger
from scrapers.base.transformers.record_transformer import RecordTransformer
from validation.records import ExportRecord


class RecordFactoryTransformer(RecordTransformer):
    def __init__(
        self,
        record_factory: Callable[[Dict[str, Any]], Any] | type,
        *,
        fallback_on_error: bool = False,
    ) -> None:
        self.record_factory = record_factory
        self.fallback_on_error = fallback_on_error
        self.logger = get_logger(self.__class__.__name__)

    def _apply_factory(self, record: ExportRecord) -> ExportRecord | Any:
        if isinstance(self.record_factory, type):
            return self.record_factory(**record)
        return self.record_factory(record)

    def transform(self, records: List[ExportRecord]) -> List[ExportRecord]:
        transformed: List[ExportRecord] = []
        for record in records:
            try:
                transformed.append(self._apply_factory(record))
            except Exception:
                if not self.fallback_on_error:
                    raise
                self.logger.warning(
                    "record_factory failed, falling back to raw record",
                    exc_info=True,
                )
                transformed.append(record)
        return transformed
