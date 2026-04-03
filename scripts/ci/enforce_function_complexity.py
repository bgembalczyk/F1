from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

from scripts.ci.git_diff import build_added_lines_map
from scripts.ci.reporting import split_csv


class _ComplexityVisitor(ast.NodeVisitor):
    CONTROL_NODES = (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.Try,
        ast.With,
        ast.AsyncWith,
        ast.Match,
    )

    BRANCH_NODES = (
        ast.If,
        ast.IfExp,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.Try,
        ast.Match,
    )

    def __init__(self) -> None:
        self.max_nesting = 0
        self.branch_count = 0
        self._depth = 0

    def generic_visit(self, node: ast.AST) -> None:
        if isinstance(node, self.BRANCH_NODES):
            self.branch_count += 1

        is_control = isinstance(node, self.CONTROL_NODES)
        if is_control:
            self._depth += 1
            self.max_nesting = max(self.max_nesting, self._depth)

        super().generic_visit(node)

        if is_control:
            self._depth -= 1


def _iter_functions(tree: ast.AST) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node)
    return functions


def _function_overlaps_added_lines(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    added_lines: set[int],
) -> bool:
    end_lineno = getattr(node, "end_lineno", node.lineno)
    return any(line in added_lines for line in range(node.lineno, end_lineno + 1))


def _function_length(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    end_lineno = getattr(node, "end_lineno", node.lineno)
    return max(1, end_lineno - node.lineno + 1)


def evaluate_file(
    path: Path,
    added_lines: set[int],
    *,
    max_function_lines: int,
    max_nesting: int,
    max_branches: int,
) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path}: unable to read file ({exc})"]

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    violations: list[str] = []
    for function in _iter_functions(tree):
        if not _function_overlaps_added_lines(function, added_lines):
            continue

        length = _function_length(function)
        visitor = _ComplexityVisitor()
        visitor.visit(function)

        if length > max_function_lines:
            violations.append(
                f"{path}:{function.lineno} function '{function.name}' length={length} > {max_function_lines}",
            )
        if visitor.max_nesting > max_nesting:
            violations.append(
                f"{path}:{function.lineno} function '{function.name}' nesting={visitor.max_nesting} > {max_nesting}",
            )
        if visitor.branch_count > max_branches:
            violations.append(
                f"{path}:{function.lineno} function '{function.name}' branching={visitor.branch_count} > {max_branches}",
            )

    return violations


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Enforce max function length/nesting/branching for changed Python functions."
        ),
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--changed-files", default="")
    parser.add_argument("--max-function-lines", type=int, default=80)
    parser.add_argument("--max-nesting", type=int, default=4)
    parser.add_argument("--max-branches", type=int, default=12)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    changed_files = [f for f in split_csv(args.changed_files) if f.endswith(".py")]
    if not changed_files:
        print("Brak zmienionych plików Python; complexity gate pominięty.")
        return 0

    added_lines_map = build_added_lines_map(args.base_sha, args.head_sha, changed_files)
    if not added_lines_map:
        print("Brak diffu dodanych linii; complexity gate pominięty.")
        return 0

    violations: list[str] = []
    for file_path in changed_files:
        path = Path(file_path)
        added_lines = added_lines_map.get(file_path, set())
        if not added_lines or not path.exists():
            continue
        violations.extend(
            evaluate_file(
                path,
                added_lines,
                max_function_lines=args.max_function_lines,
                max_nesting=args.max_nesting,
                max_branches=args.max_branches,
            ),
        )

    if not violations:
        print("Function complexity thresholds: OK")
        return 0

    print("::error::Przekroczone progi złożoności funkcji:")
    for violation in violations:
        print(f" - {violation}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
