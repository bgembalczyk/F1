from __future__ import annotations

from pathlib import Path
import sys


def ensure_project_root_on_path() -> Path:
    """Ensure repository root is available on ``sys.path``."""
    project_root = Path(__file__).resolve().parents[2]
    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    return project_root
