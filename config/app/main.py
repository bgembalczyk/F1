from dataclasses import dataclass

from app_paths.base import AppPaths
from config.app.gemini import GeminiAppConfig
from config.app.http import HttpAppConfig


@dataclass(frozen=True)
class AppConfig:
    """Kompletna konfiguracja aplikacji rozwiązywana przez provider."""

    mode: str
    paths: AppPaths
    gemini: GeminiAppConfig
    http: HttpAppConfig
