from __future__ import annotations

import ast
from pathlib import Path

CANONICAL_MODULE = "scrapers.core.domain_roles"
FORBIDDEN_MODULES = {"scrapers.base_domain_roles"}
FORBIDDEN_SYMBOLS = {"Assembler", "PipelineService"}
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__"}


def _iter_python_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*.py")
        if not any(part in SKIP_PARTS for part in path.parts)
    ]


def _forbidden_module_errors(path: Path, node: ast.ImportFrom) -> list[str]:
    if not node.module or node.module not in FORBIDDEN_MODULES:
        return []
    return [
        f"{path}:{node.lineno} forbidden import from '{node.module}', "
        f"use '{CANONICAL_MODULE}'",
    ]


def _forbidden_symbol_errors(path: Path, node: ast.ImportFrom) -> list[str]:
    if node.module != CANONICAL_MODULE:
        return []
    return [
        f"{path}:{node.lineno} forbidden role '{alias.name}' from "
        f"'{CANONICAL_MODULE}'"
        for alias in node.names
        if alias.name in FORBIDDEN_SYMBOLS
    ]


def _forbidden_import_errors(path: Path, node: ast.Import) -> list[str]:
    return [
        f"{path}:{node.lineno} forbidden import '{alias.name}', "
        f"use '{CANONICAL_MODULE}'"
        for alias in node.names
        if alias.name in FORBIDDEN_MODULES
    ]


def _check_file(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    errors: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            errors.extend(_forbidden_module_errors(path, node))
            errors.extend(_forbidden_symbol_errors(path, node))
            continue
        if isinstance(node, ast.Import):
            errors.extend(_forbidden_import_errors(path, node))
    return errors


def main() -> int:
    errors = [
        error
        for py_file in _iter_python_files(Path())
        for error in _check_file(py_file)
    ]

    if errors:
        print("[enforce_canonical_role_imports] ERROR")
        for error in errors:
            print(f"- {error}")
        return 1

    print("[enforce_canonical_role_imports] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
