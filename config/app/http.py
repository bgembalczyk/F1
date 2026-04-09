from dataclasses import dataclass


@dataclass(frozen=True)
class HttpAppConfig:
    """Konfiguracja współdzielonych klientów HTTP."""

    timeout_seconds: int
