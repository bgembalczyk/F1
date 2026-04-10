from __future__ import annotations

from pathlib import Path


def test_ci_meta_enforces_scraper_family_contracts_gate() -> None:
    workflow = Path(".github/workflows/static-quality-gates.yml").read_text(
        encoding="utf-8",
    )
    assert "scripts/ci/enforce_scraper_family_contracts.py" in workflow
    assert "tests/contract/test_scraper_family_contracts.py" in workflow
