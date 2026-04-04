from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.helpers.cell_splitting import split_cell_on_br
from scrapers.base.table.columns.helpers.engine_parsing import EngineParsingHelpers
from scrapers.base.table.columns.helpers.link_lookup import build_link_lookup
from scrapers.base.table.columns.types.base import BaseColumn

if TYPE_CHECKING:
    from scrapers.base.table.columns.context import ColumnContext


class BaseEngineColumn(BaseColumn):
    def __init__(self, *, global_config: dict[str, Any] | None = None) -> None:
        self._global_config = global_config or {}

    def _merge_engine(
        self,
        engines: list[dict[str, Any]],
        engine: dict[str, Any],
        class_value: str | None,
    ) -> None:
        has_core_data = "model" in engine or "displacement_l" in engine
        if engines and not has_core_data:
            for key, value in engine.items():
                engines[-1].setdefault(key, value)
            return

        if class_value:
            engine["class"] = class_value
        if self._global_config:
            for key, value in self._global_config.items():
                engine.setdefault(key, value)
        engines.append(engine)

    def parse(self, ctx: ColumnContext) -> Any:
        cell = ctx.cell
        if cell is None:
            return None

        segments = split_cell_on_br(cell)
        link_lookup = build_link_lookup(ctx.links or [])
        engines: list[dict[str, Any]] = []
        class_value = EngineParsingHelpers.extract_engine_class(cell)

        for segment in segments:
            engine = EngineParsingHelpers.parse_segment(
                segment,
                link_lookup,
                ctx.base_url,
            )
            if not engine:
                continue
            # If this segment has no model and no displacement it carries only
            # modifier flags (e.g. a "(Diesel)" note after a <br>). Merge those
            # flags into the preceding engine entry rather than creating a new one.
            self._merge_engine(engines, engine, class_value)

        if not engines:
            return None
        if len(engines) == 1:
            return engines[0]
        return engines
