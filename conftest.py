from __future__ import annotations

from pathlib import Path


_TARGET_MARK_EXPR = "unit or contract or architecture"
_MARKER_TOKENS = (
    "pytest.mark.unit",
    "pytest.mark.contract",
    "pytest.mark.architecture",
)


def pytest_ignore_collect(collection_path: Path, config) -> bool:  # type: ignore[no-untyped-def]
    mark_expr = (config.option.markexpr or "").strip().lower()
    if mark_expr != _TARGET_MARK_EXPR:
        return False

    if collection_path.suffix != ".py" or not collection_path.name.startswith("test_"):
        return False

    try:
        text = collection_path.read_text(encoding="utf-8")
    except OSError:
        return False

    return not any(token in text for token in _MARKER_TOKENS)
