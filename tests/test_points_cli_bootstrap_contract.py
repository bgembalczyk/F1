from __future__ import annotations

from pathlib import Path

POINTS_PACKAGE_DIR = Path("scrapers/points")


def test_points_modules_do_not_expose_main_cli_blocks() -> None:
    for file_path in sorted(POINTS_PACKAGE_DIR.glob("*.py")):
        source = file_path.read_text(encoding="utf-8")
        assert 'if __name__ == "__main__":' not in source
