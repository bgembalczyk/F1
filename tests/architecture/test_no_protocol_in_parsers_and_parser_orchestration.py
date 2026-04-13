from __future__ import annotations

import ast
from pathlib import Path

TARGET_ROOTS = (
    Path("scrapers/parsers"),
    Path("scrapers/orchestration"),
)



def test_no_typing_protocols_in_parser_layers() -> None:
    violations: list[str] = []

    for root in TARGET_ROOTS:
        for py_file in root.rglob("*.py"):
            tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module in {
                    "typing",
                    "typing_extensions",
                }:
                    for alias in node.names:
                        if alias.name == "Protocol":
                            violations.append(
                                f"{py_file}:{node.lineno} forbidden import of Protocol",
                            )

                if isinstance(node, ast.ClassDef):
                    protocol_bases = [
                        base for base in node.bases if is_protocol_base(base)
                    ]
                    if protocol_bases:
                        violations.append(
                            f"{py_file}:{node.lineno} {node.name} cannot inherit from Protocol",
                        )

    assert not violations, "\n".join(violations)
