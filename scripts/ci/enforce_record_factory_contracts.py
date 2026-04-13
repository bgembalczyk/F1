from __future__ import annotations

import ast
from pathlib import Path

SKIP_PARTS = {".git", ".venv", "venv", "__pycache__"}
FORBIDDEN_MODULE_IMPORTS = {
    "models.records.factories.compat",
    "models.records.factories.protocol2",
}
FORBIDDEN_FROM_IMPORTS = {
    "models.records.factories.compat",
    "models.records.factories.protocol2",
}
FORBIDDEN_BASE_FACTORY_SYMBOLS = {"RecordBuilderProtocol", "RecordFactoryProtocol"}


def iter_python_files(root: Path) -> list[Path]:
    return [
        path
        for path in root.rglob("*.py")
        if not any(part in SKIP_PARTS for part in path.parts)
    ]


def forbidden_import_errors(path: Path, node: ast.Import) -> list[str]:
    errors: list[str] = []
    for alias in node.names:
        if alias.name in FORBIDDEN_MODULE_IMPORTS:
            errors.append(
                f"{path}:{node.lineno} forbidden import '{alias.name}'",
            )
    return errors


def forbidden_import_from_errors(path: Path, node: ast.ImportFrom) -> list[str]:
    if not node.module:
        return []

    if node.module in FORBIDDEN_FROM_IMPORTS:
        return [
            f"{path}:{node.lineno} forbidden import from '{node.module}'",
        ]

    if node.module == "models.records.base_factory":
        forbidden_symbols = [
            alias.name
            for alias in node.names
            if alias.name in FORBIDDEN_BASE_FACTORY_SYMBOLS
        ]
        return [
            f"{path}:{node.lineno} forbidden symbol '{symbol}' from "
            "'models.records.base_factory'; use "
            "'models.records.factories.protocol'"
            for symbol in forbidden_symbols
        ]

    return []


def forbidden_create_method_errors(path: Path, tree: ast.Module) -> list[str]:
    normalized = path.as_posix()
    if not normalized.startswith("models/records/factories/"):
        return []
    if path.name == "protocol.py":
        return []
    errors: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "create":
            errors.append(
                f"{path}:{node.lineno} forbidden 'create(...)' method in record factory module",
            )
    return errors


def check_file(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return []

    errors: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            errors.extend(forbidden_import_errors(path, node))
        if isinstance(node, ast.ImportFrom):
            errors.extend(forbidden_import_from_errors(path, node))

    errors.extend(forbidden_create_method_errors(path, tree))
    return errors


def main() -> int:
    errors = [
        error
        for py_file in iter_python_files(Path())
        for error in check_file(py_file)
    ]

    if errors:
        print("[enforce_record_factory_contracts] ERROR")
        for error in errors:
            print(f"- {error}")
        return 1

    print("[enforce_record_factory_contracts] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
