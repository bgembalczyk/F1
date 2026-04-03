from __future__ import annotations

import ast
from pathlib import Path

PACKAGE_ROOTS: tuple[str, ...] = ("scrapers", "layers")
MAX_IMPORT_PATH_SEGMENTS = 7


def _iter_import_modules(py_file: Path) -> list[tuple[str, int]]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    imports: list[tuple[str, int]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((alias.name, node.lineno) for alias in node.names)
            continue

        if isinstance(node, ast.ImportFrom) and node.module:
            imports.append((node.module, node.lineno))

    return imports


def test_scrapers_and_layers_import_depth_budget() -> None:
    violations: list[str] = []

    for root in PACKAGE_ROOTS:
        for py_file in Path(root).rglob("*.py"):
            for imported_module, line_no in _iter_import_modules(py_file):
                if not imported_module.startswith(PACKAGE_ROOTS):
                    continue

                depth = imported_module.count(".") + 1
                if depth > MAX_IMPORT_PATH_SEGMENTS:
                    violations.append(
                        f"{py_file}:{line_no} imports {imported_module} "
                        f"(depth={depth})",
                    )

    assert not violations, (
        "Import path depth budget exceeded (max "
        f"{MAX_IMPORT_PATH_SEGMENTS} segments):\n" + "\n".join(sorted(violations))
    )
