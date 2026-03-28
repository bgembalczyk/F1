from __future__ import annotations

from pathlib import Path


def test_ci_meta_enforces_domain_role_contract_suite_in_quality_gate() -> None:
    workflow = Path('.github/workflows/static-quality-gates.yml').read_text(
        encoding='utf-8',
    )
    assert 'tests/test_domain_role_contracts.py' in workflow
