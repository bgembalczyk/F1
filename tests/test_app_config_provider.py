from pathlib import Path

import pytest

from config.app_config_provider import AppConfigProvider


def test_provider_prefers_env_api_key_over_file(tmp_path: Path) -> None:
    key_file = tmp_path / "gemini_api_key.txt"
    key_file.write_text("from-file", encoding="utf-8")

    provider = AppConfigProvider(
        env={
            "APP_CONFIG_DIR": str(tmp_path),
            "GEMINI_API_KEY_FILE": str(key_file),
            "GEMINI_API_KEY": "from-env",
        },
        project_root=tmp_path,
    )

    app_config = provider.get()
    assert app_config.gemini.api_key == "from-env"


def test_provider_reads_api_key_from_file_when_env_missing(tmp_path: Path) -> None:
    key_file = tmp_path / "gemini_api_key.txt"
    key_file.write_text("from-file", encoding="utf-8")

    provider = AppConfigProvider(
        env={
            "APP_CONFIG_DIR": str(tmp_path),
            "GEMINI_API_KEY_FILE": str(key_file),
        },
        project_root=tmp_path,
    )

    app_config = provider.get()
    assert app_config.gemini.api_key == "from-file"


def test_provider_raises_when_no_api_key_source(tmp_path: Path) -> None:
    provider = AppConfigProvider(
        env={"APP_CONFIG_DIR": str(tmp_path)},
        project_root=tmp_path,
    )

    with pytest.raises(FileNotFoundError, match="GEMINI_API_KEY"):
        provider.get()


def test_provider_resolves_mode_paths_and_timeouts(tmp_path: Path) -> None:
    expected_gemini_timeout = 45
    expected_http_timeout = 12
    key_file = tmp_path / "k.txt"
    key_file.write_text("k", encoding="utf-8")

    provider = AppConfigProvider(
        env={
            "APP_MODE": "production",
            "APP_CONFIG_DIR": str(tmp_path / "cfg"),
            "APP_DATA_DIR": str(tmp_path / "data"),
            "GEMINI_API_KEY_FILE": str(key_file),
            "GEMINI_TIMEOUT_SECONDS": str(expected_gemini_timeout),
            "HTTP_TIMEOUT_SECONDS": str(expected_http_timeout),
        },
        project_root=tmp_path,
    )

    app_config = provider.get()

    assert app_config.mode == "production"
    assert app_config.paths.config_dir == (tmp_path / "cfg").resolve()
    assert app_config.paths.data_dir == (tmp_path / "data").resolve()
    assert app_config.gemini.timeout_seconds == expected_gemini_timeout
    assert app_config.http.timeout_seconds == expected_http_timeout
