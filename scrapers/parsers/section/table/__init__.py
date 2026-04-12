from scrapers.parsers.section.table.base import TableSectionParser
from scrapers.parsers.section.table.contracts import SectionTableClassifierABC
from scrapers.parsers.section.table.contracts import SectionTableRecordMapperABC
from scrapers.parsers.section.table.contracts import SectionTablesHtmlParserABC

__all__ = [
    "SectionTableClassifierABC",
    "SectionTableRecordMapperABC",
    "SectionTablesHtmlParserABC",
    "TableSectionParser",
]
