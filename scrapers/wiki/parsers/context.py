from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass
class WikiParserContext:
    """Wspólny kontekst parsowania dla parserów Wikipedii."""

    source_url: str | None = None
    section_path: list[str] = field(default_factory=list)
    heading_id: str | None = None
    table_index: int | None = None
    language: str | None = None

    @classmethod
    def empty(cls) -> "WikiParserContext":
        return cls()

    def child(self, *, section_name: str | None = None, heading_id: str | None = None) -> "WikiParserContext":
        path = list(self.section_path)
        if section_name:
            path.append(section_name)
        return WikiParserContext(
            source_url=self.source_url,
            section_path=path,
            heading_id=heading_id if heading_id is not None else self.heading_id,
            table_index=self.table_index,
            language=self.language,
        )

    def for_table(self, table_index: int) -> "WikiParserContext":
        return WikiParserContext(
            source_url=self.source_url,
            section_path=list(self.section_path),
            heading_id=self.heading_id,
            table_index=table_index,
            language=self.language,
        )
