"""DOMAIN-SPECIFIC: seasons column rule moved out of base layer."""

import re

from scrapers.base.helpers.links import normalize_links
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.helpers.constants import TYRE_NAME_BY_CODE
from scrapers.base.table.columns.types.base import BaseColumn


class TyreColumn(BaseColumn):
    def parse(self, ctx: ColumnContext):
        text = (ctx.clean_text or "").strip()
        links = normalize_links(ctx.links or [], strip_marks=True, drop_empty=True)
        if links:
            tyres = []
            for link in links:
                link_text = (link.get("text") or "").strip()
                if not link_text:
                    continue
                code = link_text[0].upper()
                full_name = TYRE_NAME_BY_CODE.get(code)
                tyres.append({**link, "text": full_name or link_text})
            return tyres or None

        if not text:
            return None

        tokens = [token for token in re.split(r"[\s/,]+", text) if token]
        tyres = []
        for token in tokens:
            code = token[0].upper()
            full_name = TYRE_NAME_BY_CODE.get(code)
            tyres.append({"text": full_name or token, "url": None})
        return tyres or None
