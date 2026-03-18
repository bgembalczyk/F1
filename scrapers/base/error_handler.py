import logging
from pathlib import Path

from scrapers.base.errors import DomainParseError
from scrapers.base.errors import ScraperError
from scrapers.base.errors import ScraperNetworkError
from scrapers.base.errors import ScraperParseError
from scrapers.base.errors_report import ErrorReport
from scrapers.base.errors_report import write_error_report


class ErrorHandler:
    """Wspólna obsługa błędów scraperów (wrap + soft-skip)."""

    def __init__(
        self,
        *,
        logger: logging.Logger | logging.LoggerAdapter | None = None,
        debug_dir: Path | None = None,
        error_report_enabled: bool = False,
        run_id: str | None = None,
    ) -> None:
        self._logger = logger or logging.getLogger(__name__)
        self._debug_dir = Path(debug_dir) if debug_dir else None
        self._error_report_enabled = error_report_enabled
        self._run_id = run_id

    def set_run_id(self, run_id: str | None) -> None:
        self._run_id = run_id

    @staticmethod
    def wrap_network(
        exc: Exception,
        *,
        url: str | None = None,
    ) -> ScraperNetworkError:
        return ScraperNetworkError(
            "Błąd sieci podczas pobierania danych.",
            url=url,
            cause=exc,
        )

    @staticmethod
    def wrap_parse(exc: Exception, *, url: str | None = None) -> ScraperParseError:
        return ScraperParseError(
            "Błąd parsowania danych.",
            url=url,
            cause=exc,
        )

    def handle(self, error: ScraperError) -> bool:
        """
        Zwraca True jeśli błąd został obsłużony (soft-skip),
        False jeśli powinien być propagowany.
        """
        self._write_report(error)
        if error.critical:
            return False

        message = "Pomijam dane ze względu na błąd: %s"
        if isinstance(error, DomainParseError):
            message = "Pomijam dane domenowe ze względu na błąd: %s"
        self._logger.warning(message, error)
        return True

    def _write_report(self, error: ScraperError) -> None:
        if not self._error_report_enabled or self._debug_dir is None:
            return
        report = ErrorReport.from_exception(error, run_id=self._run_id)
        write_error_report(self._debug_dir, report)
