from __future__ import annotations

import ast
from pathlib import Path

PRODUCTION_ROOTS = (
    Path("layers"),
    Path("wiki_pipeline"),
    Path("complete_extractor"),
    Path("scrapers"),
    Path("models"),
    Path("validation"),
)

MAX_COMPAT_IMPORTS_BY_FILE: dict[str, int] = {
    "models/records/factories/base.py": 1,
    "models/records/factories/mapping.py": 1,
    "scrapers/module_naming_aliases.py": 3,
}

MAX_RECORD_FACTORY_ALIAS_BY_FILE: dict[str, int] = {
    "models/records/factories/protocol2.py": 1,
}


def _iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in PRODUCTION_ROOTS:
        if not root.exists():
            continue
        files.extend(path for path in root.rglob("*.py") if path.is_file())
    return files


def _is_compat_debt_module(module_name: str) -> bool:
    return (
        ".compat" in module_name
        or module_name.endswith("compat")
        or ".protocol2" in module_name
        or module_name.endswith("protocol2")
        or "_deprecated" in module_name
    )


def _count_compat_debt_imports(tree: ast.AST) -> int:
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_compat_debt_module(alias.name):
                    count += 1
        elif isinstance(node, ast.ImportFrom):
            if _is_compat_debt_module(node.module or ""):
                count += 1
    return count


def _count_record_factory_aliases(tree: ast.AST) -> int:
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "RecordFactory":
                    count += 1
    return count


def test_compat_debt_imports_do_not_grow() -> None:
    violations: list[str] = []
    for py_file in _iter_python_files():
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        rel = py_file.as_posix()
        count = _count_compat_debt_imports(tree)
        allowed = MAX_COMPAT_IMPORTS_BY_FILE.get(rel, 0)
        if count > allowed:
            violations.append(
                f"{rel}: compat debt imports={count}, allowed max={allowed}",
            )

    assert not violations, "\n".join(violations)


def test_record_factory_aliases_do_not_grow() -> None:
    violations: list[str] = []
    for py_file in _iter_python_files():
        source = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        rel = py_file.as_posix()
        count = _count_record_factory_aliases(tree)
        allowed = MAX_RECORD_FACTORY_ALIAS_BY_FILE.get(rel, 0)
        if count > allowed:
            violations.append(
                f"{rel}: RecordFactory aliases={count}, allowed max={allowed}",
            )

    assert not violations, "\n".join(violations)
