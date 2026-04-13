#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
from pathlib import Path

SKIP_PARTS = {".git", ".venv", "venv", "__pycache__"}
ROOT = Path(__file__).resolve().parents[2]


def merge_base() -> str:
    result = subprocess.run(
        ["git", "merge-base", "origin/main", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() or "HEAD~1"


def iter_changed_python_files(base_ref: str) -> list[Path]:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "--diff-filter=AM",
            base_ref,
            "HEAD",
            "--",
            "*.py",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return [
        ROOT / rel
        for rel in result.stdout.splitlines()
        if rel and not any(part in SKIP_PARTS for part in Path(rel).parts)
    ]


def defined_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
            continue
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
            continue
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
            continue
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
            continue
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                names.add(alias.asname or alias.name)
    return names


def extract_all_symbols(tree: ast.Module) -> list[str] | None:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        ):
            continue
        if not isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
            return None
        symbols: list[str] = []
        for item in node.value.elts:
            if isinstance(item, ast.Constant) and isinstance(item.value, str):
                symbols.append(item.value)
                continue
            return None
        return symbols
    return None


def check_file(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [f"{path}:{exc.lineno} syntax error blocks export analysis"]

    exported = extract_all_symbols(tree)
    if exported is None:
        return []

    defined = defined_names(tree)
    errors: list[str] = []
    for symbol in exported:
        if symbol not in defined:
            errors.append(
                f"{path} broken export in __all__: '{symbol}' is not defined/imported",
            )
    return errors


def main() -> int:
    base_ref = merge_base()
    errors = [
        error
        for py_file in iter_changed_python_files(base_ref)
        for error in check_file(py_file)
    ]
    if errors:
        print("[enforce_no_broken_exports] ERROR")
        for error in errors:
            print(f"- {error}")
        return 1
    print("[enforce_no_broken_exports] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
