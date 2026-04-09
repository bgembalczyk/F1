from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.base.helpers.links import normalize_links
from scrapers.base.helpers.text import clean_wiki_text
from scrapers.base.table.columns.types.auto import AutoColumn
from scrapers.base.table.columns.types.base import BaseColumn

if TYPE_CHECKING:
    from scrapers.base.table.columns.context import ColumnContext


class ConstructorNameColumn(BaseColumn):
    """Parses constructor names, preserving multi-name aliases split by '/'."""

    def __init__(self) -> None:
        self._auto_column = AutoColumn()

    @staticmethod
    def _split_names(text: str) -> list[str]:
        names = [part.strip() for part in text.split("/") if part.strip()]
        deduped: list[str] = []
        for name in names:
            if name not in deduped:
                deduped.append(name)
        return deduped

    def parse(self, ctx: ColumnContext) -> Any:
        links = normalize_links(ctx.links or [], drop_empty=True)
        clean_text = clean_wiki_text(ctx.clean_text or ctx.raw_text or "")

        if links and len(links) > 1 and "/" in clean_text:
            names = self._split_names(
                " / ".join(str(link.get("text") or "").strip() for link in links),
            )
            common_url = links[0].get("url")
            if not common_url or any(link.get("url") != common_url for link in links):
                common_url = None

            payload: dict[str, Any] = {"names": names}
            if common_url:
                payload["url"] = common_url
            return payload

        if not links and "/" in clean_text:
            names = self._split_names(clean_text)
            if len(names) > 1:
                return {"names": names}

        return self._auto_column.parse(ctx)
