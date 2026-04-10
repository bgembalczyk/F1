from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppPaths:
    """Rozwiązane ścieżki aplikacji."""

    project_root: Path
    config_dir: Path
    data_dir: Path
    gemini_api_key_file: Path
