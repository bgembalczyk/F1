from typing import Any
from typing import Dict

from scrapers.base.helpers.parsing import parse_configuration
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class EngineConfigurationColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Dict[str, Any] | None:
        return parse_configuration(ctx)
