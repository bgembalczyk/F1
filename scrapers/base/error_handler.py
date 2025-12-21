from __future__ import annotations

import logging
from typing import Optional

from scrapers.base.errors import ScraperNetworkError, ScraperParseError


class ErrorHandler:
    """Wspólna obsługa błędów scraperów (wrap + soft-skip)."""

    def __init__(self, *, logger: Optional[logging.Logger] = None) -> None:
        self._logger = logger or logging.getLogger(__name__)

    def wrap_network(
        self, exc: Exception, *, url: Optional[str] = None
    ) -> ScraperNetworkError:
        return ScraperNetworkError(
            "Błąd sieci podczas pobierania danych.",
            url=url,
            cause=exc,
        )

    def wrap_parse(
        self, exc: Exception, *, url: Optional[str] = None
    ) -> ScraperParseError:
        return ScraperParseError(
            "Błąd parsowania danych.",
            url=url,
            cause=exc,
        )

    def handle(self, error: Exception) -> bool:
        """
        Zwraca True jeśli błąd został obsłużony (soft-skip),
        False jeśli powinien być propagowany.
        """
        critical = bool(getattr(error, "critical", False))
        if critical:
            return False

        self._logger.warning("Pomijam dane ze względu na błąd: %s", error)
        return True
