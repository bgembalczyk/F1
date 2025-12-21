from typing import Any

from scrapers.base.helpers.text import strip_marks
from scrapers.base.table.columns.context import ColumnContext
from scrapers.base.table.columns.registry import column_type_registry
from scrapers.base.table.columns.types.base import BaseColumn


@column_type_registry.register("driver")
class DriverColumn(BaseColumn):
    """
    Kolumna specjalna dla kierowcy / ridera:
    - ignoruje flagi (typowo pierwszy link bez tekstu albo z tekstem typu kraju),
    - preferuje ostatni link z niepustym tekstem (najczęściej kierowca),
    - jeśli nie ma sensownych linków, używa clean_text jako samego nazwiska.
    """

    def parse(self, ctx: ColumnContext) -> Any:
        # 1) Spróbuj znaleźć link z niepustym tekstem, patrząc od końca
        if ctx.links:
            for raw_link in reversed(ctx.links):
                link = dict(raw_link)
                txt = strip_marks(link.get("text") or "")
                if txt:
                    return {"text": txt, "url": link.get("url")}

        # 2) Fallback: sam tekst (np. gdy kierowca nie jest podlinkowany
        #    albo w komórce jest tylko plain text)
        if ctx.clean_text:
            txt = strip_marks(ctx.clean_text)
            if txt:
                return {"text": txt}

        return None
