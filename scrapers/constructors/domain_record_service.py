from __future__ import annotations

from typing import Any

from scrapers.constructors.postprocess.assembler import ConstructorRecordAssembler
from scrapers.constructors.postprocess.assembler import ConstructorRecordDTO
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser


class DomainRecordService:
    def __init__(
        self,
        *,
        assembler: ConstructorRecordAssembler | None = None,
        article_tables_parser: ArticleTablesParser | None = None,
    ) -> None:
        self._assembler = assembler or ConstructorRecordAssembler()
        self._article_tables_parser = article_tables_parser or ArticleTablesParser()

    def extract_tables(self, soup: Any) -> list[dict[str, Any]]:
        return self._article_tables_parser.parse(soup)

    def assemble_record(
        self,
        *,
        url: str,
        infoboxes: list[dict[str, Any]],
        tables: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self._assembler.assemble(
            payload=ConstructorRecordDTO(
                url=url,
                infoboxes=infoboxes,
                tables=tables,
                sections=sections,
            ),
        )
