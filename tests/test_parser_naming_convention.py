from __future__ import annotations

import ast
from pathlib import Path


def _parser_classes_without_parse(root: Path) -> list[str]:
    issues: list[str] = []
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if not node.name.endswith("Parser"):
                continue
            methods = {
                child.name
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            }
            if "parse" not in methods:
                issues.append(f"{path}:{node.name}")
    return issues


def test_infobox_driver_parser_classes_require_parse_entrypoint() -> None:
    root = Path("scrapers/infobox/parsers/drivers")
    issues = _parser_classes_without_parse(root)
    assert issues == []
