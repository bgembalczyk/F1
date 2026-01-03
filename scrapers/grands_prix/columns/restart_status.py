from typing import Any
from typing import Dict

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.grands_prix.helpers.restart_status import restart_status


class RestartStatusColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> Dict[str, Any] | None:
        return restart_status(ctx)
