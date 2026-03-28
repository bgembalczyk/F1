from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.contracts import ColumnParseResult
from scrapers.base.table.columns.contracts import normalize_column_parse_result
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

    def parse(self, ctx: ColumnContext) -> ColumnParseResult:
        # opcjonalnie - zwraca dict; niekoniecznie używane
        result: dict[str, object] = {}
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
            parsed = normalize_column_parse_result(
                col.parse(subctx),
                skip_sentinel=ctx.skip_sentinel,
            )
            if not parsed.skip:
                result[new_key] = parsed.value
        return ColumnParseResult.from_value(result)

    def apply(self, ctx: ColumnContext, record: dict[str, object]) -> None:
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
