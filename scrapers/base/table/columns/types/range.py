import re
from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class RangeColumn(BaseColumn):
    """
    Kolumna parsująca zakres (min/max) z tej samej komórki.

    lower_column/upper_column mogą być dowolnymi kolumnami (int, float, unit, ...).
    Zwraca dict: {"min": ..., "max": ...}.
    """

    def __init__(
        self,
        lower_column: BaseColumn,
        upper_column: BaseColumn,
        *,
        separator_pattern: str = r"\s*(?:–|-|—|−)\s*",
        shared_suffix: str | None = None,
    ) -> None:
        self.lower_column = lower_column
        self.upper_column = upper_column
        self.separator_pattern = re.compile(separator_pattern)
        self.shared_suffix = shared_suffix

    def parse(self, ctx: ColumnContext) -> Any:
        text = (ctx.clean_text or "").replace("\xa0", " ")
        if not text:
            return None

        parts = self.separator_pattern.split(text, maxsplit=1)
        if len(parts) == 1:
            lower_text = upper_text = parts[0]
        else:
            lower_text, upper_text = parts

        lower_text = self._apply_shared_suffix(lower_text)
        upper_text = self._apply_shared_suffix(upper_text)

        lower_ctx = ColumnContext(
            header=ctx.header,
            key=ctx.key,
            raw_text=lower_text,
            clean_text=lower_text,
            links=ctx.links,
            cell=ctx.cell,
            skip_sentinel=ctx.skip_sentinel,
            model_fields=ctx.model_fields,
        )
        upper_ctx = ColumnContext(
            header=ctx.header,
            key=ctx.key,
            raw_text=upper_text,
            clean_text=upper_text,
            links=ctx.links,
            cell=ctx.cell,
            skip_sentinel=ctx.skip_sentinel,
            model_fields=ctx.model_fields,
        )

        return {
            "min": self.lower_column.parse(lower_ctx),
            "max": self.upper_column.parse(upper_ctx),
        }

    def _apply_shared_suffix(self, text: str) -> str:
        if not self.shared_suffix:
            return text.strip()

        suffix = self.shared_suffix.strip()
        if not suffix:
            return text.strip()

        if re.search(rf"{re.escape(suffix)}\b", text, flags=re.IGNORECASE):
            return text.strip()

        return f"{text.strip()} {suffix}".strip()
