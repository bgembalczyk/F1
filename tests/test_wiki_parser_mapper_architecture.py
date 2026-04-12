from __future__ import annotations

import ast
from pathlib import Path

CONTRACT_FILES = [
    Path("scrapers/parsers/roles.py"),
    Path("scrapers/parsers/wiki/families.py"),
    Path("scrapers/parsers/wiki/domain_mapper.py"),
]


def _class_defs(path: Path) -> list[ast.ClassDef]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return [node for node in tree.body if isinstance(node, ast.ClassDef)]


def _has_method(node: ast.ClassDef, method_name: str) -> bool:
    return any(
        isinstance(member, ast.FunctionDef) and member.name == method_name
        for member in node.body
    )


def test_parser_contract_classes_define_parse() -> None:
    violations: list[str] = []
    for path in CONTRACT_FILES:
        for cls in _class_defs(path):
            if cls.name.endswith("Parser") or cls.name.endswith("ParserABC"):
                if not _has_method(cls, "parse"):
                    violations.append(f"{path}:{cls.name}")
    assert not violations, "Parser contract without parse: " + ", ".join(violations)


def test_mapper_contract_classes_define_map() -> None:
    violations: list[str] = []
    for path in CONTRACT_FILES:
        for cls in _class_defs(path):
            if cls.name.endswith("Mapper") or cls.name.endswith("MapperABC"):
                if not _has_method(cls, "map"):
                    violations.append(f"{path}:{cls.name}")
    assert not violations, "Mapper contract without map: " + ", ".join(violations)


def test_no_mapper_in_parser_field() -> None:
    root = Path(__file__).resolve().parents[1]
    violations: list[str] = []
    for path in sorted((root / "scrapers" / "parsers").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                if node.target.id.endswith("_parser") and "Mapper" in ast.unparse(node.annotation):
                    violations.append(f"{path}:{node.target.id}")
            if isinstance(node, ast.Assign):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
                for name in names:
                    if name.endswith("_parser") and "Mapper" in ast.unparse(node.value):
                        violations.append(f"{path}:{name}")
    assert not violations, "Mapper assigned to *_parser fields: " + ", ".join(violations)
