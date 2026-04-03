from __future__ import annotations

from pathlib import Path

SCRAPERS_DIR = Path("scrapers")


def test_scrapers_package_has_no_standalone_main_blocks() -> None:
    files_with_main: list[str] = []
    for file_path in sorted(SCRAPERS_DIR.rglob("*.py")):
        source = file_path.read_text(encoding="utf-8")
        if 'if __name__ == "__main__":' in source:
            files_with_main.append(str(file_path))

    assert files_with_main == []
