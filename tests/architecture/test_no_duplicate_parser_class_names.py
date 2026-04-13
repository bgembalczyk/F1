from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

PARSER_ROOT = Path("scrapers/parsers")


def test_no_duplicate_parser_class_names_in_scrapers_parsers() -> None:
    parser_classes: dict[str, list[tuple[Path, int]]] = defaultdict(list)

    for file_path in sorted(PARSER_ROOT.rglob("*.py")):
        module = ast.parse(
            file_path.read_text(encoding="utf-8"),
            filename=str(file_path),
        )
        for node in module.body:
            if not isinstance(node, ast.ClassDef) or not node.name.endswith("Parser"):
                continue
            parser_classes[node.name].append((file_path, node.lineno))

    duplicates = {
        name: sorted(locations)
        for name, locations in parser_classes.items()
        if len(locations) > 1
    }

    assert not duplicates, (
        "Duplicate parser class names are forbidden in scrapers/parsers:\n"
        + "\n".join(
            f"- {name}: " + ", ".join(f"{path}:{lineno}" for path, lineno in locations)
            for name, locations in sorted(duplicates.items())
        )
    )
