from __future__ import annotations

from scrapers.parsers.contracts.mapping import WikiDomainMapperABC


class WikiDomainMapper(WikiDomainMapperABC):
    """Default parser/domain boundary mapper (identity transport)."""

    def map(self, raw: dict[str, object]) -> dict[str, object]:
        return dict(raw)


__all__ = ["WikiDomainMapper"]
