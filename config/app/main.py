from dataclasses import dataclass

from config.app.gemini import GeminiAppConfig
from config.app.http import HttpAppConfig
from config.app_paths import AppPaths


@dataclass(frozen=True)
class AppConfig:
    """Kompletna konfiguracja aplikacji rozwiązywana przez provider."""

    mode: str
    paths: AppPaths
    gemini: GeminiAppConfig
    http: HttpAppConfig
