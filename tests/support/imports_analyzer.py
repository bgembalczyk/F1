from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ParsedImport:
    module: str
    level: int


def parse_imports(py_file: Path) -> list[ParsedImport]:
    """Return only factual imports declared via Import/ImportFrom nodes."""
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    imports: list[ParsedImport] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(ParsedImport(module=alias.name, level=0) for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.append(ParsedImport(module=node.module, level=node.level))

    return imports
