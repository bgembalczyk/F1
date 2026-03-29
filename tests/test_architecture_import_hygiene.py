from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

ARCHITECTURE_TEST_FILES = (
    Path("tests/test_architecture_import_rules.py"),
    Path("tests/test_section_architecture_boundaries.py"),
    Path("tests/test_domain_entrypoint_boundaries.py"),
    Path("tests/architecture/rules.py"),
)


def _module_import_keys(tree: ast.Module) -> list[tuple[str, int]]:
    keys: list[tuple[str, int]] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            key = "import " + ", ".join(
                f"{alias.name} as {alias.asname}" if alias.asname else alias.name
                for alias in node.names
            )
            keys.append((key, node.lineno))
            continue

        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = ", ".join(
                f"{alias.name} as {alias.asname}" if alias.asname else alias.name
                for alias in node.names
            )
            key = f"from {'.' * node.level}{module} import {names}"
            keys.append((key, node.lineno))

    return keys


def _imported_names(tree: ast.Module) -> dict[str, int]:
    imported: dict[str, int] = {}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported[alias.asname or alias.name.split(".")[-1]] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                imported[alias.asname or alias.name] = node.lineno
    return imported


def _reassigned_imports(tree: ast.Module) -> list[tuple[str, int, int]]:
    imported = _imported_names(tree)
    reassignments: list[tuple[str, int, int]] = []

    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets.extend(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets.append(node.target)
        else:
            continue

        for target in targets:
            if isinstance(target, ast.Name) and target.id in imported:
                reassignments.append((target.id, imported[target.id], node.lineno))

    return reassignments


def test_architecture_tests_have_no_duplicate_import_statements() -> None:
    duplicates: dict[str, list[tuple[str, list[int]]]] = {}

    for test_file in ARCHITECTURE_TEST_FILES:
        tree = ast.parse(test_file.read_text(encoding="utf-8"), filename=str(test_file))
        grouped: dict[str, list[int]] = defaultdict(list)

        for key, lineno in _module_import_keys(tree):
            grouped[key].append(lineno)

        file_duplicates = [
            (key, lines)
            for key, lines in grouped.items()
            if len(lines) > 1
        ]
        if file_duplicates:
            duplicates[str(test_file)] = sorted(file_duplicates)

    assert not duplicates, f"Duplicate import statements found: {duplicates}"


def test_architecture_tests_do_not_reassign_imported_names() -> None:
    violations: dict[str, list[tuple[str, int, int]]] = {}

    for test_file in ARCHITECTURE_TEST_FILES:
        tree = ast.parse(test_file.read_text(encoding="utf-8"), filename=str(test_file))
        reassignments = _reassigned_imports(tree)
        if reassignments:
            violations[str(test_file)] = reassignments

    assert not violations, f"Reassigned imported names in architecture tests: {violations}"
