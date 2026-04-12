from typing import Any


class DomainMapperABC:
    """Mapuje parsed payload wiki na rekordy domenowe."""

    def map(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
