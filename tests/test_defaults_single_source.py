from __future__ import annotations

import ast
from pathlib import Path

CRITICAL_DEFAULT_LITERALS = {"../../data/wiki", "../../data/debug"}

CRITICAL_DEFAULT_SOURCE = Path("scrapers/base/defaults.py")
SCRAPERS_ROOT = Path("scrapers")


def test_critical_path_defaults_are_defined_once() -> None:
    offenders: list[str] = []

    for py_file in SCRAPERS_ROOT.rglob("*.py"):
        if py_file == CRITICAL_DEFAULT_SOURCE:
            continue
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        duplicated: list[str] = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            if node.value in CRITICAL_DEFAULT_LITERALS:
                duplicated.append(node.value)
        if duplicated:
            offenders.append(f"{py_file}: {sorted(set(duplicated))}")

    assert not offenders, (
        "Critical path defaults should be imported from scrapers.base.defaults, "
        "not duplicated as local literals.\n"
        + "\n".join(offenders)
    )


def test_no_local_none_fallback_for_shared_run_config_profile() -> None:
    domain_entrypoint_source = Path("scrapers/base/domain_entrypoint.py").read_text(
        encoding="utf-8",
    )

    assert "run_config or config.run_config_profile()" not in domain_entrypoint_source
