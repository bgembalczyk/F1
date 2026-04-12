from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

ROLE_FILE = Path("scrapers/parsers/roles.py")


def _module_ast() -> ast.Module:
    return ast.parse(ROLE_FILE.read_text(encoding="utf-8"))


def _class_defs(module: ast.Module) -> list[ast.ClassDef]:
    return [node for node in module.body if isinstance(node, ast.ClassDef)]


def _base_name(base: ast.expr) -> str | None:
    if isinstance(base, ast.Name):
        return base.id
    if isinstance(base, ast.Attribute):
        return base.attr
    if isinstance(base, ast.Subscript):
        return _base_name(base.value)
    return None


def _is_abc_class(class_def: ast.ClassDef) -> bool:
    return any(_base_name(base) == "ABC" for base in class_def.bases)


def test_roles_has_no_duplicate_abc_class_names() -> None:
    classes = _class_defs(_module_ast())
    abc_names = [class_def.name for class_def in classes if _is_abc_class(class_def)]
    duplicates = sorted(name for name, count in Counter(abc_names).items() if count > 1)
    assert duplicates == []


def test_roles_all_exports_existing_symbols() -> None:
    module = _module_ast()
    existing_symbols = {
        node.name
        for node in module.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }
    existing_symbols.update(
        target.id
        for node in module.body
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
    )
    existing_symbols.update(
        alias.asname or alias.name.split(".")[-1]
        for node in module.body
        if isinstance(node, ast.Import)
        for alias in node.names
    )
    existing_symbols.update(
        alias.asname or alias.name
        for node in module.body
        if isinstance(node, ast.ImportFrom)
        for alias in node.names
    )

    all_assign = next(
        node
        for node in module.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets)
    )
    assert isinstance(all_assign.value, ast.List)

    exported = [
        element.value
        for element in all_assign.value.elts
        if isinstance(element, ast.Constant) and isinstance(element.value, str)
    ]
    missing = sorted(symbol for symbol in exported if symbol not in existing_symbols)
    assert missing == []


def test_roles_parser_abcs_define_parse_method() -> None:
    parser_classes = [
        class_def
        for class_def in _class_defs(_module_ast())
        if class_def.name.endswith("ParserABC") and _is_abc_class(class_def)
    ]

    missing_parse = [
        class_def.name
        for class_def in parser_classes
        if not any(isinstance(node, ast.FunctionDef) and node.name == "parse" for node in class_def.body)
    ]
    assert missing_parse == []
