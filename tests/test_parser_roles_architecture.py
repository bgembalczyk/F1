from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

CONTRACTS_DIR = Path("scrapers/parsers/contracts")


def _contract_module_paths() -> list[Path]:
    return sorted(
        path for path in CONTRACTS_DIR.glob("*.py") if path.name != "__init__.py"
    )


def _module_ast(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _class_defs(module: ast.Module) -> list[ast.ClassDef]:
    return [node for node in module.body if isinstance(node, ast.ClassDef)]


def test_contract_modules_have_no_duplicate_class_names_per_module() -> None:
    for path in _contract_module_paths():
        names = [class_def.name for class_def in _class_defs(_module_ast(path))]
        duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
        assert duplicates == [], f"{path}: duplicate class definitions: {duplicates}"
