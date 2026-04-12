"""Re-export: parser type aliases at scrapers.wiki.parsers.types path."""
from models.data.parsed.header import HeaderParsedData
from models.data.parsed.paragraph import ParagraphParsedData
from models.data.parsed.table import TableParsedData
from models.payload import WikiParsedPayload

__all__ = [
    "HeaderParsedData",
    "ParagraphParsedData",
    "TableParsedData",
    "WikiParsedPayload",
]
