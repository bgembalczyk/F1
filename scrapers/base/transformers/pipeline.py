from typing import List
from typing import Sequence

from scrapers.base.logging import get_logger
from scrapers.base.transformers.record_transformer import RecordTransformer
from validation.records import ExportRecord


class TransformersPipeline:
    def __init__(
            self,
            transformers: Sequence[RecordTransformer],
            *,
            logger=None,
    ) -> None:
        self.transformers = list(transformers)
        self.logger = logger or get_logger(self.__class__.__name__)

    def apply(self, records: List[ExportRecord]) -> List[ExportRecord]:
        transformed = list(records)
        for transformer in self.transformers:
            before_count = len(transformed)
            self.logger.debug(
                "Transformer %s: before=%d",
                transformer.__class__.__name__,
                before_count,
            )
            transformed = transformer.transform(transformed)
            self.logger.debug(
                "Transformer %s: after=%d",
                transformer.__class__.__name__,
                len(transformed),
            )
        return transformed
