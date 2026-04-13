from __future__ import annotations

from typing import Any


class WikiDomainMapper:
    """Default parser/domain boundary mapper (identity transport)."""

    def map(self, raw: dict[str, object]) -> dict[str, object]:
        return dict(raw)


__all__ = ["WikiDomainMapper"]
