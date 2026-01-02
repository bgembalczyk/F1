import re
from typing import Any

from bs4 import BeautifulSoup, Tag

from models.records.link import LinkRecord
from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text_normalization import clean_wiki_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers import build_engine_link_lookup
from scrapers.base.table.columns.helpers import extract_engine_class
from scrapers.base.table.columns.helpers import parse_engine_segment
from scrapers.base.table.columns.helpers import replace_link_breaks
from scrapers.base.table.columns.helpers import split_engine_cell_on_br
from scrapers.base.table.columns.types.base import BaseColumn


class EngineColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return None

        segments = split_engine_cell_on_br(cell)
        link_lookup = build_engine_link_lookup(ctx.links or [])
        engines: list[dict[str, Any]] = []
        class_value = extract_engine_class(cell)

        for segment in segments:
            engine = parse_engine_segment(segment, link_lookup)
            if engine:
                if class_value:
                    engine["class"] = class_value
                engines.append(engine)

        if not engines:
            return None
        if len(engines) == 1:
            return engines[0]
        return engines




