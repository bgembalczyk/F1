from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Any

if TYPE_CHECKING:
    from scrapers.base.contracts import RecordAssemblerProtocol

from scrapers.constructors.constructors_postprocess.assembler import ConstructorRecordAssembler
from scrapers.constructors.constructors_postprocess.assembler import ConstructorRecordDTO
from scrapers.services.domain_record.base import BaseDomainRecordService
from scrapers.wiki.parsers.elements.article_tables import ArticleTablesParser


@dataclass(frozen=True, slots=True)
class ConstructorDomainRecordInput:
    url: str
    infoboxes: list[dict[str, Any]]
    tables: list[dict[str, Any]]
    sections: list[dict[str, Any]]


class ConstructorDomainRecordService(
    BaseDomainRecordService[ConstructorDomainRecordInput]
):
    def __init__(
        self,
        *,
        assembler: RecordAssemblerProtocol[ConstructorRecordDTO] | None = None,
        article_tables_parser: ArticleTablesParser | None = None,
    ) -> None:
        self._assembler = assembler or ConstructorRecordAssembler()
        self._article_tables_parser = article_tables_parser or ArticleTablesParser()

    def extract_tables(self, soup: Any) -> list[dict[str, Any]]:
        return self._article_tables_parser.parse(soup)

    def assemble_record(self, payload: ConstructorDomainRecordInput) -> dict[str, Any]:
        return self._assembler.assemble(
            ConstructorRecordDTO(
                url=payload.url,
                infoboxes=payload.infoboxes,
                tables=payload.tables,
                sections=payload.sections,
            ),
        )


class DomainRecordService(ConstructorDomainRecordService):
    """Compatibility alias for legacy imports."""
