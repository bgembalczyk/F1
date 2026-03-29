from __future__ import annotations

from pathlib import Path

_TARGET_MARKERS = ("unit", "contract", "architecture")


def _wants_gate_subset(markexpr: str) -> bool:
    normalized = markexpr.replace(" ", "")
    if not normalized:
        return False
    return any(marker in normalized for marker in _TARGET_MARKERS)


def _has_any_target_marker(test_file: Path) -> bool:
    try:
        content = test_file.read_text(encoding="utf-8")
    except OSError:
        return False

    return any(f"pytest.mark.{marker}" in content for marker in _TARGET_MARKERS)


def pytest_ignore_collect(collection_path: Path, config) -> bool:  # type: ignore[no-untyped-def]
    markexpr = getattr(config.option, "markexpr", "") or ""
    if not _wants_gate_subset(markexpr):
        return False

    if collection_path.name == "conftest.py":
        return False

    if collection_path.suffix != ".py" or "tests" not in collection_path.parts:
        return False

    return not _has_any_target_marker(collection_path)
