from typing import Any

from scrapers.columns.context import ColumnContext


class EnumMarksMixin:
    """
    Mixin/base dla kolumn parsujących wartości enum
    na podstawie znaków (np. *, †) w raw_text.

    Używany wyłącznie jako mixin w dziedziczeniu wielokrotnym.

    mapping: znak -> wartość enum
    default: wartość gdy żaden znak nie pasuje
    """

    def __init__(
        self,
        mapping: dict[str, Any] | None = None,
        default: Any = None,
        **kwargs: Any,
    ) -> None:
        del kwargs
        if mapping is not None:
            self.mapping = dict(mapping)
            self.default = default

    def parse_marks(
        self,
        ctx: ColumnContext,
        mapping: dict[str, Any] | None = None,
        default: Any = None,
    ) -> Any:
        marks_mapping = self.mapping if mapping is None else mapping
        fallback = self.default if mapping is None else default
        text = ctx.raw_text or ""
        for mark, value in marks_mapping.items():
            if mark in text:
                return value
        return fallback

__all__ = ["EnumMarksMixin"]
