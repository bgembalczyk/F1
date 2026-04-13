from scrapers.columns.base import BaseColumn
from scrapers.columns.context import ColumnContext
from scrapers.constants.constants_points import ROLE_PATTERN
from scrapers.helpers.parsing import parse_int_from_text


class FirstPlaceColumn(BaseColumn):
    def parse(self, ctx: ColumnContext) -> int | dict | None:
        value = parse_int_from_text(ctx.clean_text)
        if value is None:
            return None

        role_match = ROLE_PATTERN.search(ctx.clean_text)
        if role_match:
            role = "driver" if role_match.group(1).lower() == "d" else "constructor"
            return {"value": value, "role": role}

        return value
