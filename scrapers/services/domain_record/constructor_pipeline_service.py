from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any

from scrapers.constructors.constructors_postprocess.assembler import (
    ConstructorRecordAssembler,
)
from scrapers.constructors.constructors_postprocess.assembler import (
    ConstructorRecordDTO,
)
from scrapers.services.domain_record.base_pipeline_service import BaseFactoryScraper
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssemblerProtocol


class ConstructorPipelineService(BaseFactoryScraper[ConstructorRecordDTO]):
    required_fields = ("url", "infoboxes", "tables", "sections")

    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[ConstructorRecordDTO] | None = None,
        article_tables_parser: ArticleTablesParser | None = None,
    ) -> None:
        self._assembler = assembler or ConstructorRecordAssembler()
        self._article_tables_parser = article_tables_parser or ArticleTablesParser()

    def extract_tables(self, soup: Any) -> list[dict[str, Any]]:
        return self.with_retry(lambda: self._article_tables_parser.parse(soup))

    def _build_payload(self, source: dict[str, Any]) -> ConstructorRecordDTO:
        return ConstructorRecordDTO(
            url=str(source["url"]),
            infoboxes=list(source["infoboxes"]),
            tables=list(source["tables"]),
            sections=list(source["sections"]),
        )

    def _assemble(self, payload: ConstructorRecordDTO) -> dict[str, Any]:
        return self._assembler.assemble(payload)

    def assemble_record(
        self,
        *,
        url: str,
        infoboxes: list[dict[str, Any]],
        tables: list[dict[str, Any]],
        sections: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self.run(
            {
                "url": url,
                "infoboxes": infoboxes,
                "tables": tables,
                "sections": sections,
            },
        )
