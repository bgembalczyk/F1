from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR_NAMES: tuple[str, ...] = (
    "layers",
    "scrapers",
    "models",
    "infrastructure",
    "validation",
    "complete_extractor",
)
SOURCE_DIRS: tuple[Path, ...] = tuple(PROJECT_ROOT / name for name in SOURCE_DIR_NAMES)


def iter_python_files(paths: Iterable[Path]) -> Iterator[Path]:
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            yield path
            continue
        if path.is_dir():
            yield from path.rglob("*.py")
