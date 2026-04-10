from __future__ import annotations

import ast
from pathlib import Path

PRODUCTION_ROOTS = (Path("layers"), Path("wiki_pipeline"), Path("complete_extractor"), Path("scrapers"))
ALLOWED_LEGACY_ROOT = Path("scrapers/legacy")


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in PRODUCTION_ROOTS:
        files.extend(path for path in root.rglob("*.py") if path.is_file())
    return files


def _imports_legacy_module(node: ast.AST) -> bool:
    if isinstance(node, ast.Import):
        return any(alias.name.startswith("scrapers.legacy") for alias in node.names)
    if isinstance(node, ast.ImportFrom):
        return (node.module or "").startswith("scrapers.legacy")
    return False


def test_production_modules_do_not_import_scrapers_legacy() -> None:
    violations: list[str] = []

    for py_file in _iter_python_files():
        if py_file.is_relative_to(ALLOWED_LEGACY_ROOT):
            continue

        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            # Legacy files with syntax issues are outside this rule scope.
            continue
        for node in ast.walk(tree):
            if _imports_legacy_module(node):
                violations.append(str(py_file))
                break

    assert not violations, f"Production imports from scrapers.legacy are forbidden: {violations}"
