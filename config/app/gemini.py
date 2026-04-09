from dataclasses import dataclass


@dataclass(frozen=True)
class GeminiAppConfig:
    """Konfiguracja modułu Gemini."""

    api_key: str
    timeout_seconds: int
