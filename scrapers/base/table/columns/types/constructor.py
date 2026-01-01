from __future__ import annotations

from bs4 import Tag

from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.base.table.columns.types.constructor_part import ConstructorPartColumn


class ConstructorColumn(BaseColumn):
    def parse(self, ctx: ColumnContext):
        has_line_break = ctx.cell.find("br") is not None if ctx.cell else False
        if has_line_break:
            line_contexts = _split_constructor_lines(ctx)
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


def _split_constructor_lines(ctx: ColumnContext) -> list[ColumnContext]:
    if not ctx.cell:
        return []

    lines: list[list[object]] = [[]]
    for child in ctx.cell.children:
        if isinstance(child, Tag) and child.name == "br":
            lines.append([])
            continue
        lines[-1].append(child)

    if not lines:
        return []

    line_link_counts = []
    for line in lines:
        link_count = 0
        for node in line:
            if isinstance(node, Tag):
                if node.name == "a":
                    link_count += 1
                else:
                    link_count += len(node.find_all("a"))
        line_link_counts.append(link_count)

    line_contexts: list[ColumnContext] = []
    link_index = 0
    for line, link_count in zip(lines, line_link_counts):
        line_links = ctx.links[link_index : link_index + link_count]
        link_index += link_count

        text_parts = []
        for node in line:
            if isinstance(node, Tag):
                node_text = node.get_text(" ", strip=True)
            else:
                node_text = str(node).strip()
            if node_text:
                text_parts.append(node_text)
        line_text = " ".join(text_parts).strip()
        clean_text = clean_wiki_text(line_text)

        if not clean_text and not line_links:
            continue

        line_contexts.append(
            ColumnContext(
                header=ctx.header,
                key=ctx.key,
                raw_text=line_text,
                clean_text=clean_text,
                links=line_links,
                cell=None,
                skip_sentinel=ctx.skip_sentinel,
                model_fields=ctx.model_fields,
            )
        )

    return line_contexts
