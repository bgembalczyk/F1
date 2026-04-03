from __future__ import annotations

import ast
from pathlib import Path

LAYER_INFRA_EXCEPTIONS = {
    "layers/application.py",
}


def _iter_imported_modules(py_file: Path) -> list[tuple[str, int]]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    imported: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend((alias.name, node.lineno) for alias in node.names)
            continue

        if isinstance(node, ast.ImportFrom) and node.module:
            imported.append((node.module, node.lineno))

    return imported


def test_layers_do_not_import_infrastructure_outside_composition_root() -> None:
    violations: list[str] = []

    for py_file in Path("layers").rglob("*.py"):
        file_key = py_file.as_posix()
        if file_key in LAYER_INFRA_EXCEPTIONS:
            continue

        for module_name, line_no in _iter_imported_modules(py_file):
            if module_name.startswith("infrastructure"):
                violations.append(f"{file_key}:{line_no} -> {module_name}")

    assert not violations, (
        "Only composition root may bind infrastructure to layers. "
        "Move concrete dependencies behind interfaces/adapters. "
        f"violations={sorted(violations)}"
    )
