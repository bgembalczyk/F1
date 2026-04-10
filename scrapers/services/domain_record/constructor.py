from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssemblerProtocol

from scrapers.constructors.constructors_postprocess.assembler import ConstructorRecordAssembler
from scrapers.constructors.constructors_postprocess.assembler import ConstructorRecordDTO
from scrapers.services.domain_record._shared import DomainRecordResult
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser


@dataclass(frozen=True, slots=True)
class ConstructorDomainRecordInput:
    url: str
    soup: Any
    infoboxes: list[dict[str, Any]]
    sections: list[dict[str, Any]]


class DomainRecordService:
    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[ConstructorRecordDTO] | None = None,
        article_tables_parser: ArticleTablesParser | None = None,
    ) -> None:
        self._assembler = assembler or ConstructorRecordAssembler()
        self._article_tables_parser = article_tables_parser or ArticleTablesParser()

    def execute(self, payload: ConstructorDomainRecordInput) -> DomainRecordResult:
        return DomainRecordResult(
            record=self._assembler.assemble(
                ConstructorRecordDTO(
                    url=payload.url,
                    infoboxes=payload.infoboxes,
                    tables=self._extract_tables(payload.soup),
                    sections=payload.sections,
                ),
            ),
        )

    def _extract_tables(self, soup: Any) -> list[dict[str, Any]]:
        return self._article_tables_parser.parse(soup)
