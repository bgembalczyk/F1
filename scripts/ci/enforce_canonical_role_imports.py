from __future__ import annotations

import ast
from pathlib import Path

CANONICAL_MODULE = "scrapers.core.domain_roles"
FORBIDDEN_MODULES = {"scrapers.base_domain_roles"}
FORBIDDEN_SYMBOLS: set[str] = set()
SKIP_PARTS = {".git", ".venv", "venv", "__pycache__"}
CANONICAL_ROLE_IMPORTS: dict[str, str] = {
    "scrapers.runner": "scrapers.runners.scraper_runner",
    "scrapers.pipeline_runner": "scrapers.runners.pipeline_runner",
    "scrapers.domain_entrypoint": "scrapers.entrypoints.domain_entrypoint_service",
}
THIN_COMPAT_MODULES = {
    Path("scrapers/runner.py"),
    Path("scrapers/pipeline_runner.py"),
    Path("scrapers/domain_entrypoint.py"),
}


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
    errors: list[str] = []
    for alias in node.names:
        if alias.name in FORBIDDEN_MODULES:
            errors.append(
                f"{path}:{node.lineno} forbidden import '{alias.name}', "
                f"use '{CANONICAL_MODULE}'",
            )
        if alias.name in CANONICAL_ROLE_IMPORTS:
            errors.append(
                f"{path}:{node.lineno} forbidden import '{alias.name}', "
                f"use '{CANONICAL_ROLE_IMPORTS[alias.name]}'",
            )
    return errors


def _canonical_role_errors(path: Path, node: ast.ImportFrom) -> list[str]:
    if not node.module:
        return []
    if node.module not in CANONICAL_ROLE_IMPORTS:
        return []
    return [
        f"{path}:{node.lineno} forbidden import from '{node.module}', "
        f"use '{CANONICAL_ROLE_IMPORTS[node.module]}'",
    ]


def _is_thin_compat_statement(node: ast.stmt) -> bool:
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return True
    if isinstance(node, ast.Expr):
        return isinstance(node.value, (ast.Constant, ast.Call))
    if isinstance(node, ast.Assign):
        return any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        )
    return False


def _thin_module_errors(path: Path, tree: ast.Module) -> list[str]:
    rel = Path(path.as_posix())
    if rel not in THIN_COMPAT_MODULES:
        return []
    violations = [
        node.lineno for node in tree.body if not _is_thin_compat_statement(node)
    ]
    if not violations:
        return []
    return [
        f"{path}:{lineno} compatibility module must stay thin "
        "(imports, warning, __all__ only)"
        for lineno in violations
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
            errors.extend(_canonical_role_errors(path, node))
            continue
        if isinstance(node, ast.Import):
            errors.extend(_forbidden_import_errors(path, node))
    errors.extend(_thin_module_errors(path, tree))
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
