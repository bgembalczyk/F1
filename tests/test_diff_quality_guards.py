# ruff: noqa: SLF001
from __future__ import annotations


from scripts.ci import enforce_diff_quality_guards as guards
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def test_broad_exception_requires_justification_annotation(
    tmp_path: Path,
    monkeypatch,
) -> None:
    test_file = tmp_path / "sample.py"
    test_file.write_text(
        "try:\n    pass\nexcept Exception:\n    pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)

    violations = guards._check_broad_exceptions_with_justification({"sample.py": {3}})

    assert len(violations) == 1
    assert "justified-exception" in violations[0].message


def test_broad_exception_with_marker_is_allowed(tmp_path: Path, monkeypatch) -> None:
    test_file = tmp_path / "sample.py"
    test_file.write_text(
        "try:\n    pass\n"
        "except Exception:  # justified-exception: normalization boundary\n"
        "    pass\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(guards, "REPO_ROOT", tmp_path)

    violations = guards._check_broad_exceptions_with_justification({"sample.py": {3}})

    assert violations == []


def test_registry_implementation_drift_check_passes_for_current_repo() -> None:
    assert guards._check_registry_implementation_drift() == []
