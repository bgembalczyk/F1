from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from typing import Callable
from typing import TypeVar

T = TypeVar("T")


class RetryMixin:
    """Mixin zapewniający ponawianie akcji z błędem przejściowym."""

    retries = 1

    def with_retry(self, fn: Callable[[], T], *, retries: int | None = None) -> T:
        attempts = (retries if retries is not None else self.retries) + 1
        last_error: Exception | None = None
        for _ in range(attempts):
            try:
                return fn()
            except Exception as exc:  # pragma: no cover - defensywne
                last_error = exc
        if last_error is None:  # pragma: no cover - sanity fallback
            raise RuntimeError("RetryMixin exhausted without captured exception")
        raise last_error


class DebugDumpMixin:
    """Mixin zapisujący diagnostyczny dump payloadu i wyniku pipeline."""

    debug_dir: str | Path | None = None

    def dump_debug_payload(self, *, payload: dict[str, Any], stem: str) -> None:
        if self.debug_dir is None:
            return
        output_dir = Path(self.debug_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / f"{stem}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


class ValidationMixin:
    """Mixin walidujący obecność wymaganych pól payloadu."""

    def validate_required(self, payload: dict[str, Any], required_fields: tuple[str, ...]) -> None:
        missing = [field for field in required_fields if payload.get(field) is None]
        if missing:
            msg = f"Missing required fields: {', '.join(missing)}"
            raise ValueError(msg)
