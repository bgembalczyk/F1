from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class MultiColumn(BaseColumn):
    """
    Kompozycyjny MultiColumn: jedna komórka -> wiele pól w rekordzie.

    Przykład:
        MultiColumn({
            "circuit": UrlColumn(),
            "circuit_status": EnumColumn(mapping),
        })
    """

    def __init__(self, subcolumns: dict[str, BaseColumn]) -> None:
        self.subcolumns = subcolumns

    def parse(self, ctx: ColumnContext) -> Any:
        # opcjonalnie – zwraca dict; niekoniecznie używane
        result: dict[str, Any] = {}
        for new_key, col in self.subcolumns.items():
            subctx = ColumnContext(
                header=ctx.header,
                key=new_key,
                raw_text=ctx.raw_text,
                clean_text=ctx.clean_text,
                links=ctx.links,
                cell=ctx.cell,
                base_url=ctx.base_url,
                skip_sentinel=ctx.skip_sentinel,
                model_fields=ctx.model_fields,
                header_link=ctx.header_link,
            )
            val = col.parse(subctx)
            if val is not ctx.skip_sentinel:
                result[new_key] = val
        return result

    def apply(self, ctx: ColumnContext, record: dict[str, Any]) -> None:
        for new_key, col in self.subcolumns.items():
            subctx = ColumnContext(
                header=ctx.header,
                key=new_key,
                raw_text=ctx.raw_text,
                clean_text=ctx.clean_text,
                links=ctx.links,
                cell=ctx.cell,
                base_url=ctx.base_url,
                skip_sentinel=ctx.skip_sentinel,
                model_fields=ctx.model_fields,
                header_link=ctx.header_link,
            )
            col.apply(subctx, record)
