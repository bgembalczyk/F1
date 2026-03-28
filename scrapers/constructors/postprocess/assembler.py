from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from models.value_objects import WikiUrl
from scrapers.wiki.parsers.elements.article_table_model import ArticleTableModel


@dataclass(frozen=True)
class ConstructorRecordDTO:
    url: WikiUrl | str
    infoboxes: list[dict[str, Any]]
    tables: list[ArticleTableModel]
    sections: list[dict[str, Any]]


class ConstructorRecordAssembler:
    def assemble(
        self,
        *,
        payload: ConstructorRecordDTO,
    ) -> dict[str, Any]:
        url = WikiUrl.from_raw(payload.url)
        return {
            "url": url.to_export(),
            "infoboxes": payload.infoboxes,
            "tables": payload.tables,
            "sections": payload.sections,
        }
