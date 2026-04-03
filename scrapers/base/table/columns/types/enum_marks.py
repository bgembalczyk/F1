from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class EnumMarksMixin(BaseColumn):
    """
    Mixin/base dla kolumn parsujących wartości enum
    na podstawie znaków (np. *, †) w raw_text.

    Może być używany jako samodzielna kolumna
    lub jako mixin w dziedziczeniu wielokrotnym.

    mapping: znak -> wartość enum
    default: wartość gdy żaden znak nie pasuje
    """

    def __init__(
        self,
        mapping: dict[str, Any] | None = None,
        default: Any = None,
        **kwargs: Any,
    ) -> None:
        if mapping is not None:
            self.mapping = dict(mapping)
            self.default = default
        super().__init__(**kwargs)

    def parse(self, ctx: ColumnContext) -> Any:
        text = ctx.raw_text or ""
        for mark, value in self.mapping.items():
            if mark in text:
                return value
        return self.default


# Backward-compatible alias
EnumMarksColumn = EnumMarksMixin
