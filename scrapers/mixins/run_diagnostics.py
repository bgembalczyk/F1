from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from typing import Callable
from typing import TypeVar

from bs4 import BeautifulSoup

from scrapers.base.errors import ScraperError
from scrapers.base.errors import ScraperNetworkError
from scrapers.base.errors import ScraperParseError

T = TypeVar("T")


class RunDiagnosticsMixin:
    """Cross-cutting runtime diagnostics: retry, debug dump, validation and stage wrappers."""

    retries = 1
    debug_dir: str | Path | None = None

    def with_retry(self, fn: Callable[[], T], *, retries: int | None = None) -> T:
        attempts = (retries if retries is not None else self.retries) + 1
        last_error: Exception | None = None
        for _ in range(attempts):
            try:
                return fn()
            except Exception as exc:  # pragma: no cover - defensive
                last_error = exc
        if last_error is None:  # pragma: no cover - sanity fallback
            raise RuntimeError("Retry loop finished without captured exception")
        raise last_error

    def dump_debug_payload(self, *, payload: dict[str, Any], stem: str) -> None:
        if self.debug_dir is None:
            return
        output_dir = Path(self.debug_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{stem}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def validate_required(
        self,
        payload: dict[str, Any],
        required_fields: tuple[str, ...],
    ) -> None:
        missing = [field for field in required_fields if payload.get(field) is None]
        if missing:
            msg = f"Missing required fields: {', '.join(missing)}"
            raise ValueError(msg)

    def run_with_error_handling(
        self,
        fetch_fn: Callable[[], str],
        parse_fn: Callable[[BeautifulSoup], T],
    ) -> T | None:
        html = self._run_fetch_stage(fetch_fn)
        if html is None:
            return None
        return self._run_parse_stage(parse_fn, html)

    def _run_fetch_stage(self, fetch_fn: Callable[[], str]) -> str | None:
        try:
            return fetch_fn()
        except Exception as exc:  # noqa: BLE001
            return self._handle_stage_error(
                exc=exc,
                error=self._network_stage_error(exc),
            )

    def _run_parse_stage(
        self,
        parse_fn: Callable[[BeautifulSoup], T],
        html: str,
    ) -> T | None:
        try:
            soup = BeautifulSoup(html, "html.parser")
            return parse_fn(soup)
        except Exception as exc:  # noqa: BLE001
            return self._handle_stage_error(
                exc=exc,
                error=self._parse_stage_error(exc),
            )

    def _network_stage_error(self, exc: Exception) -> ScraperError:
        if isinstance(exc, ScraperError):
            return exc
        return self._wrap_network_error(exc)

    def _parse_stage_error(self, exc: Exception) -> ScraperError:
        if isinstance(exc, ScraperError):
            return exc
        return self._wrap_parse_error(exc)

    def _handle_stage_error(
        self,
        *,
        exc: Exception,
        error: ScraperError,
    ) -> None:
        if self._handle_scraper_error(error):
            return
        if error is exc:
            raise exc
        raise error from exc

    # contracts for host base class
    def _wrap_network_error(self, exc: Exception) -> ScraperNetworkError:
        raise NotImplementedError

    def _wrap_parse_error(self, exc: Exception) -> ScraperParseError:
        raise NotImplementedError

    def _handle_scraper_error(self, error: ScraperError) -> bool:
        raise NotImplementedError
