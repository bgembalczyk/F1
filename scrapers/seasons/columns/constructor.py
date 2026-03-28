"""DOMAIN-SPECIFIC: seasons column rule (constructor split) localized for seasons domain."""

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.constructor_parsing import (
    ConstructorParsingHelpers,
)
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.seasons.columns.constructor_part import ConstructorPartColumn


class ConstructorColumn(BaseColumn):
    def parse(self, ctx: ColumnContext):
        has_line_break = ctx.cell.find("br") is not None if ctx.cell else False
        if has_line_break:
            line_contexts = ConstructorParsingHelpers.split_lines(ctx)
            parsed_lines = []
            for line_ctx in line_contexts:
                data = self._parse_constructor_data(line_ctx)
                if data:
                    parsed_lines.append(data)
            if parsed_lines:
                return parsed_lines
        data = self._parse_constructor_data(ctx)
        return data or None

    @staticmethod
    def _parse_constructor_data(ctx: ColumnContext) -> dict[str, object]:
        """Parses constructor data from a single context (line or full cell)."""
        split_index = ConstructorParsingHelpers.find_hyphen_split_index(ctx)
        if split_index is not None and ctx.links:
            pre_links = ctx.links[:split_index]
            post_links = ctx.links[split_index:]
            chassis_text = " ".join(
                link.get("text", "") for link in pre_links if link.get("text")
            )
            chassis: dict[str, object] | None = (
                {"text": chassis_text, "url": None} if chassis_text else None
            )
            engine = post_links[0] if post_links else None
            data: dict[str, object] = {}
            if chassis is not None:
                data["chassis_constructor"] = chassis
            if engine is not None:
                data["engine_constructor"] = engine
            return data

        chassis = ConstructorPartColumn(0).parse(ctx)
        engine = ConstructorPartColumn(1).parse(ctx)
        data = {}
        if chassis is not None:
            data["chassis_constructor"] = chassis
        if engine is not None:
            data["engine_constructor"] = engine
        return data
