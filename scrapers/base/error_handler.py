import logging
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar

from scrapers.base.error_codes import resolve_error_code
from scrapers.base.errors import DomainParseError
from scrapers.base.errors import ErrorBehavior
from scrapers.base.errors import ScraperError
from scrapers.base.errors import ScraperNetworkError
from scrapers.base.errors import ScraperParseError
from scrapers.base.errors import ScraperValidationError
from scrapers.base.errors_report import ErrorReport
from scrapers.base.errors_report import write_error_report
from scrapers.base.errors_report import write_error_summary_by_code

T = TypeVar("T")


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

    def _resolve_run_id(self, run_id: str | None) -> str | None:
        return run_id if run_id is not None else self._run_id

    def wrap_network(
        self,
        exc: Exception,
        *,
        url: str | None = None,
        section_id: str | None = None,
        parser_name: str | None = None,
        run_id: str | None = None,
    ) -> ScraperNetworkError:
        return ScraperNetworkError(
            "Błąd sieci podczas pobierania danych.",
            url=url,
            section_id=section_id,
            parser_name=parser_name,
            run_id=self._resolve_run_id(run_id),
            cause=exc,
        )

    def wrap_parse(
        self,
        exc: Exception,
        *,
        url: str | None = None,
        section_id: str | None = None,
        parser_name: str | None = None,
        run_id: str | None = None,
    ) -> ScraperParseError:
        return ScraperParseError(
            "Błąd parsowania danych.",
            url=url,
            section_id=section_id,
            parser_name=parser_name,
            run_id=self._resolve_run_id(run_id),
            cause=exc,
        )

    def wrap_validation(
        self,
        exc: Exception,
        *,
        url: str | None = None,
        section_id: str | None = None,
        parser_name: str | None = None,
        run_id: str | None = None,
    ) -> ScraperValidationError:
        return ScraperValidationError(
            "Błąd walidacji danych.",
            url=url,
            section_id=section_id,
            parser_name=parser_name,
            run_id=self._resolve_run_id(run_id),
            cause=exc,
        )

    def wrap_domain_parse(
        self,
        exc: Exception,
        *,
        message: str,
        url: str | None = None,
        section_id: str | None = None,
        parser_name: str | None = None,
        run_id: str | None = None,
    ) -> DomainParseError:
        return DomainParseError(
            message,
            url=url,
            section_id=section_id,
            parser_name=parser_name,
            run_id=self._resolve_run_id(run_id),
            cause=exc,
        )

    @staticmethod
    def run_with_policy(
        fn: Callable[[], T],
        *,
        wrapper: Callable[[Exception], ScraperError],
        catch: tuple[type[Exception], ...] = (Exception,),
    ) -> T:
        try:
            return fn()
        except catch as exc:
            raise wrapper(exc) from exc

    @classmethod
    def run_domain_parse(
        cls,
        fn: Callable[[], T],
        *,
        message: str,
        url: str | None = None,
        section_id: str | None = None,
        parser_name: str | None = None,
        run_id: str | None = None,
    ) -> T:
        handler = cls(run_id=run_id)
        return cls.run_with_policy(
            fn,
            wrapper=lambda exc: handler.wrap_domain_parse(
                exc,
                message=message,
                url=url,
                section_id=section_id,
                parser_name=parser_name,
                run_id=run_id,
            ),
            catch=(TypeError, ValueError),
        )

    def handle(self, error: ScraperError) -> bool:
        """
        Zwraca True jeśli błąd został obsłużony (soft-skip),
        False jeśli powinien być propagowany.
        """
        self._write_report(error)
        if error.behavior == ErrorBehavior.HARD:
            return False

        code_definition = resolve_error_code(error.code)
        self._logger.warning(
            "Soft-skip [%s|%s]: %s | "
            "context(url=%s, section_id=%s, parser=%s, run_id=%s)",
            code_definition.code_id,
            code_definition.short_description,
            error,
            error.url,
            error.section_id,
            error.parser_name,
            self._resolve_run_id(None),
        )
        return True

    def _write_report(self, error: ScraperError) -> None:
        if not self._error_report_enabled or self._debug_dir is None:
            return
        report = ErrorReport.from_exception(error, run_id=self._resolve_run_id(None))
        write_error_report(self._debug_dir, report)
        write_error_summary_by_code(
            self._debug_dir,
            run_id=self._resolve_run_id(None),
        )
