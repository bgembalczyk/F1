from typing import Any

from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.background_mixin import BackgroundMixin
from scrapers.base.table.columns.types.base import BaseColumn
from scrapers.races.helpers.restart_status import restart_status


class RestartStatusColumn(BackgroundMixin, BaseColumn):
    def parse(self, ctx: ColumnContext) -> dict[str, Any] | None:
        return restart_status(ctx)
