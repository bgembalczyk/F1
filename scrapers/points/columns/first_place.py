import re

from scrapers.base.helpers.parsing import parse_int_from_text
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.types.base import BaseColumn


class FirstPlaceColumn(BaseColumn):
    _ROLE_PATTERN = re.compile(r"\(\s*([dc])\s*\)", re.IGNORECASE)

    def parse(self, ctx: ColumnContext) -> int | dict | None:
        value = parse_int_from_text(ctx.clean_text)
        if value is None:
            return None

        role_match = self._ROLE_PATTERN.search(ctx.clean_text)
        if role_match:
            role = "driver" if role_match.group(1).lower() == "d" else "constructor"
            return {"value": value, "role": role}

        return value
