"""Centralny provider konfiguracji aplikacji.

Źródła konfiguracji (priorytet malejący):
1. Zmienne środowiskowe.
2. Lokalne pliki konfiguracyjne.
3. Wartości domyślne z kodu.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from infrastructure.gemini.constants import DEFAULT_TIMEOUT
from infrastructure.http_client.policies.constants import DEFAULT_HTTP_TIMEOUT

DEFAULT_APP_MODE = "development"


@dataclass(frozen=True)
class AppPaths:
    """Rozwiązane ścieżki aplikacji."""

    project_root: Path
    config_dir: Path
    data_dir: Path
    gemini_api_key_file: Path


@dataclass(frozen=True)
class GeminiAppConfig:
    """Konfiguracja modułu Gemini."""

    api_key: str
    timeout_seconds: int


@dataclass(frozen=True)
class HttpAppConfig:
    """Konfiguracja współdzielonych klientów HTTP."""

    timeout_seconds: int


@dataclass(frozen=True)
class AppConfig:
    """Kompletna konfiguracja aplikacji rozwiązywana przez provider."""

    mode: str
    paths: AppPaths
    gemini: GeminiAppConfig
    http: HttpAppConfig


class AppConfigProvider:
    """Dostarcza zunifikowaną konfigurację dla całej aplikacji."""

    def __init__(
        self,
        *,
        env: dict[str, str] | None = None,
        project_root: Path | None = None,
    ) -> None:
        self._env = dict(env) if env is not None else dict(os.environ)
        self._project_root = (
            project_root.resolve()
            if project_root is not None
            else Path(__file__).resolve().parents[1]
        )

    def get(self) -> AppConfig:
        paths = self.get_paths()
        return AppConfig(
            mode=self.get_mode(),
            paths=paths,
            gemini=self.get_gemini_config(),
            http=self.get_http_config(),
        )

    def get_paths(self) -> AppPaths:
        config_dir = self._read_path(
            "APP_CONFIG_DIR",
            default=self._project_root / "config",
        )
        data_dir = self._read_path("APP_DATA_DIR", default=self._project_root / "data")
        gemini_api_key_file = self._read_path(
            "GEMINI_API_KEY_FILE",
            default=config_dir / "gemini_api_key.txt",
        )
        return AppPaths(
            project_root=self._project_root,
            config_dir=config_dir,
            data_dir=data_dir,
            gemini_api_key_file=gemini_api_key_file,
        )

    def get_mode(self) -> str:
        return self._env.get("APP_MODE", DEFAULT_APP_MODE).strip() or DEFAULT_APP_MODE

    def get_gemini_config(self) -> GeminiAppConfig:
        paths = self.get_paths()
        return GeminiAppConfig(
            api_key=self._resolve_gemini_api_key(paths),
            timeout_seconds=self._read_int(
                "GEMINI_TIMEOUT_SECONDS",
                default=DEFAULT_TIMEOUT,
            ),
        )

    def get_http_config(self) -> HttpAppConfig:
        return HttpAppConfig(
            timeout_seconds=self._read_int(
                "HTTP_TIMEOUT_SECONDS",
                default=DEFAULT_HTTP_TIMEOUT,
            ),
        )

    def _resolve_gemini_api_key(self, paths: AppPaths) -> str:
        from_env = self._env.get("GEMINI_API_KEY", "").strip()
        if from_env:
            return from_env

        if paths.gemini_api_key_file.exists():
            return paths.gemini_api_key_file.read_text(encoding="utf-8").strip()

        msg = (
            "Brak konfiguracji GEMINI_API_KEY: ustaw zmienną "
            "środowiskową GEMINI_API_KEY "
            f"albo utwórz plik z kluczem: {paths.gemini_api_key_file}"
        )
        raise FileNotFoundError(msg)

    def _read_int(self, key: str, *, default: int) -> int:
        raw = self._env.get(key)
        if raw is None or not raw.strip():
            return default
        try:
            value = int(raw)
        except ValueError as exc:
            msg = f"Niepoprawna wartość całkowita w {key}: {raw!r}"
            raise ValueError(msg) from exc
        if value <= 0:
            msg = f"Wartość {key} musi być > 0, otrzymano: {value}"
            raise ValueError(msg)
        return value

    def _read_path(self, key: str, *, default: Path) -> Path:
        raw = self._env.get(key)
        if raw is None or not raw.strip():
            return default.resolve()
        return Path(raw).expanduser().resolve()
