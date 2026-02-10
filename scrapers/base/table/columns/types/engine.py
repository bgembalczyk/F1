from typing import Any

from scrapers.base.helpers.cell_splitting import split_cell_on_br
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.engine_parsing import EngineParsingHelpers
from scrapers.base.table.columns.types.base import BaseColumn


class EngineColumn(BaseColumn):
    def __init__(self, *, global_config: dict[str, Any] | None = None) -> None:
        self._global_config = global_config or {}

    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return None

        segments = split_cell_on_br(cell)
        link_lookup = EngineParsingHelpers.build_link_lookup(ctx.links or [])
        engines: list[dict[str, Any]] = []
        class_value = EngineParsingHelpers.extract_engine_class(cell)

        for segment in segments:
            engine = EngineParsingHelpers.parse_segment(segment, link_lookup)
            if engine:
                if class_value:
                    engine["class"] = class_value
                if self._global_config:
                    for key, value in self._global_config.items():
                        engine.setdefault(key, value)
                engines.append(engine)

        if not engines:
            return None
        if len(engines) == 1:
            return engines[0]
        return engines
