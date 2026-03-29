from __future__ import annotations

from typing import Any

from scripts.ci.duplicate_report import DuplicateFilter
from scripts.ci.duplicate_report import DuplicateNormalizer
from scripts.ci.duplicate_report import MarkdownRenderer


def test_duplicate_normalizer_maps_supported_keys() -> None:
    normalizer = DuplicateNormalizer()

    payload: dict[str, Any] = {
        "firstFile": {"path": "a.py", "startLoc": 10, "endLoc": 12},
        "secondFile": {"name": "b.py", "start": 20, "end": 25},
        "codefragment": "\nprint('x')\n",
    }

    normalized = normalizer.normalize(payload)

    assert normalized == {
        "first": {"name": "a.py", "start": 10, "end": 12},
        "second": {"name": "b.py", "start": 20, "end": 25},
        "fragment": "print('x')",
    }


def test_duplicate_filter_returns_only_overlapping_duplicates(monkeypatch: Any) -> None:
    duplicate_filter = DuplicateFilter()

    def fake_added_lines(
        _base_sha: str,
        _head_sha: str,
        _changed_files: list[str],
    ) -> dict[str, set[int]]:
        return {"src/app.py": {10, 11}}

    monkeypatch.setattr(
        "scripts.ci.duplicate_report.build_added_lines_map",
        fake_added_lines,
    )

    duplicates = [
        {
            "first": {"name": "src/app.py", "start": 9, "end": 10},
            "second": {"name": "src/other.py", "start": 1, "end": 2},
            "fragment": "x",
        },
        {
            "first": {"name": "src/app.py", "start": 30, "end": 31},
            "second": {"name": "src/other.py", "start": 1, "end": 2},
            "fragment": "y",
        },
    ]

    result = duplicate_filter.filter_new_duplicates(
        duplicates,
        "base",
        "head",
        ["src/app.py"],
    )

    assert result == [duplicates[0]]


def test_markdown_renderer_renders_duplicates_list_and_status() -> None:
    renderer = MarkdownRenderer()
    duplicates = [
        {
            "first": {"name": "src/a.py", "start": 1, "end": 2},
            "second": {"name": "src/b.py", "start": 3, "end": 4},
            "fragment": "a = 1\nb = 2",
        },
    ]

    markdown = renderer.render(duplicates, warn_threshold=1, fail_threshold=2)

    assert "⚠️ Wykryto **1** nowych duplikatów" in markdown
    assert "`src/a.py` (L1-L2) ↔ `src/b.py` (L3-L4)" in markdown
    assert "```python" in markdown
