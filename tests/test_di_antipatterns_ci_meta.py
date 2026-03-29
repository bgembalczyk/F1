from __future__ import annotations

from pathlib import Path


def test_ci_meta_enforces_di_antipattern_ast_check_with_adr_binding() -> None:
    workflow = Path(".github/workflows/static-quality-gates.yml").read_text(
        encoding="utf-8",
    )
    assert "scripts/ci/check_di_antipatterns.py" in workflow
    assert "grep -E '^(layers/|scrapers/base/).+\\.py$'" in workflow
    assert "scripts/check_di_antipatterns.py" in workflow
    assert "grep -E '^(layers/|scrapers/base/|scrapers/drivers/infobox/).+\\.py$'" in workflow
    assert "--adr-reference-text" in workflow
