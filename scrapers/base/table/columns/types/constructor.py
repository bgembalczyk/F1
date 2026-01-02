from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers import split_constructor_lines
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.columns.types.constructor_part import ConstructorPartColumn


class ConstructorColumn(BaseColumn):
    def parse(self, ctx: ColumnContext):
        has_line_break = ctx.cell.find("br") is not None if ctx.cell else False
        if has_line_break:
            line_contexts = split_constructor_lines(ctx)
            parsed_lines = []
            for line_ctx in line_contexts:
                chassis = ConstructorPartColumn(0).parse(line_ctx)
                engine = ConstructorPartColumn(1).parse(line_ctx)
                data: dict[str, object] = {}
                if chassis is not None:
                    data["chassis_constructor"] = chassis
                if engine is not None:
                    data["engine_constructor"] = engine
                if data:
                    parsed_lines.append(data)
            if parsed_lines:
                return parsed_lines
        chassis = ConstructorPartColumn(0).parse(ctx)
        engine = ConstructorPartColumn(1).parse(ctx)
        data: dict[str, object] = {}
        if chassis is not None:
            data["chassis_constructor"] = chassis
        if engine is not None:
            data["engine_constructor"] = engine
        return data or None


