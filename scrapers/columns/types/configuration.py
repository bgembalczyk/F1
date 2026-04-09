from typing import Any

from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.helpers.parsing import parse_configuration


class EngineConfigurationColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> dict[str, Any] | None:
        return parse_configuration(ctx)


__all__ = ["EngineConfigurationColumn"]
