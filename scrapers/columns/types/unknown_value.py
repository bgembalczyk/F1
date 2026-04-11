from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext


class UnknownValueColumn(BaseColumn):
    DEFAULT_UNKNOWN_VALUE = "unknown"

    def __init__(
        self,
        inner: BaseColumn,
        *,
        unknown_value: str | None = None,
    ) -> None:
        self.inner = inner
        self.unknown_token = unknown_value or self.DEFAULT_UNKNOWN_VALUE

    def parse(self, ctx: ColumnContext):
        text = (ctx.clean_text or "").strip()
        if text == "?":
            return self.unknown_token
        return self.inner.parse(ctx)
