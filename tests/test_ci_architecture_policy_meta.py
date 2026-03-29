from __future__ import annotations

from pathlib import Path


def test_static_quality_gate_includes_new_architecture_policy_checks() -> None:
    workflow = Path(".github/workflows/static-quality-gates.yml").read_text(encoding="utf-8")

    assert "scripts/ci/adr_reference_check.py" in workflow
    assert "scripts/ci/architecture_registry_consistency.py" in workflow
    assert "scripts/ci/mypy_scope_regression.py" in workflow
    assert "Duplicate blocks check" in workflow
    assert "No new architectural debt policy" in workflow
