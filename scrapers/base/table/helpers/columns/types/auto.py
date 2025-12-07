from typing import Any

from scrapers.base.table.helpers.columns.context import ColumnContext
from scrapers.base.table.helpers.columns.types.base import BaseColumn


class AutoColumn(BaseColumn):
    """
    Domyślne zachowanie:
    - clean_text,
    - jeśli jest dokładnie 1 link → dict{text, url},
    - jeśli wiele linków i tylko przecinki między nimi → lista linków.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        value: Any = ctx.clean_text

        links = ctx.links
        if len(links) == 1:
            return links[0]

        if len(links) > 1:
            # spróbuj wykryć przypadek "link, link, link"
            import re

            raw_html = "".join(str(x) for x in ctx.cell.contents)
            cleaned_html = re.sub(r"\s+|&nbsp;|\xa0", "", raw_html)
            tmp = cleaned_html
            for a in ctx.cell.find_all("a", href=True):
                link_html = re.sub(r"\s+|&nbsp;|\xa0", "", str(a))
                tmp = tmp.replace(link_html, "")

            if all(ch == "," for ch in tmp if ch != ""):
                return links

        return value
