from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from scripts.ci.structural_quality_exceptions import MAX_FUNCTION_LINES_EXCEPTIONS
from scripts.ci.structural_quality_exceptions import REDUNDANT_ALIAS_EXCEPTIONS


class StructuralVisitor(ast.NodeVisitor):
    def __init__(self, *, file_path: str) -> None:
        self.file_path = file_path
        self.function_violations: list[tuple[str, int, int]] = []
        self.class_violations: list[tuple[str, int, int]] = []
        self.alias_violations: list[tuple[str, int, str]] = []

    @staticmethod
    def _node_length(node: ast.AST) -> int:
        start = getattr(node, "lineno", 1)
        end = getattr(node, "end_lineno", start)
        return max(1, end - start + 1)

    @staticmethod
    def _is_private_name(name: str) -> bool:
        return name.startswith("_")

    @staticmethod
    def _is_private_attribute_call(call: ast.Call) -> bool:
        func = call.func
        if not isinstance(func, ast.Attribute):
            return False
        owner = func.value
        return isinstance(owner, ast.Attribute) and owner.attr.startswith("_")

    def _is_redundant_alias_body(  # noqa: C901, PLR0911
        self,
        function: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> bool:
        body = function.body
        if not body:
            return False

        filtered: list[ast.stmt] = []
        for stmt in body:
            if (
                isinstance(stmt, ast.Expr)
                and isinstance(stmt.value, ast.Constant)
                and isinstance(stmt.value.value, str)
            ):
                continue
            filtered.append(stmt)

        if len(filtered) != 1:
            return False

        stmt = filtered[0]
        call: ast.Call | None = None
        if isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Call):  # noqa: SIM114
            call = stmt.value
        elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
            call = stmt.value

        if call is None:
            return False

        if self._is_private_name(function.name):
            return False

        called = call.func
        if isinstance(called, ast.Name) and self._is_private_name(called.id):
            return False
        if isinstance(called, ast.Attribute) and self._is_private_name(called.attr):
            return False
        return not self._is_private_attribute_call(call)

    def _visit_function_common(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        length = self._node_length(node)
        length_limit = MAX_FUNCTION_LINES_EXCEPTIONS.get(
            (self.file_path, node.name),
            self.max_function_lines,
        )
        if length > length_limit:
            self.function_violations.append((node.name, node.lineno, length))
        if (
            self._is_redundant_alias_body(node)
            and (self.file_path, node.name) not in REDUNDANT_ALIAS_EXCEPTIONS
        ):
            self.alias_violations.append(
                (node.name, node.lineno, ast.unparse(node.body[-1])),
            )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function_common(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function_common(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        length = self._node_length(node)
        if length > self.max_class_lines:
            self.class_violations.append((node.name, node.lineno, length))
        self.generic_visit(node)


def _should_skip(path: Path) -> bool:
    ignored_parts = {".venv", ".git", "__pycache__", "data", "tests"}
    return any(part in ignored_parts for part in path.parts)


def _iter_python_files(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(item) for item in paths if item.endswith(".py")]

    all_files = Path().rglob("*.py")
    return [path for path in all_files if not _should_skip(path)]


def evaluate_file(
    path: Path,
    *,
    max_function_lines: int,
    max_class_lines: int,
    max_file_lines: int,
) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{path}: unable to read ({exc})"]

    file_line_count = len(source.splitlines())
    violations: list[str] = []
    if file_line_count > max_file_lines:
        violations.append(f"{path}: file length={file_line_count} > {max_file_lines}")

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return violations

    visitor = StructuralVisitor(file_path=path.as_posix())
    visitor.max_function_lines = max_function_lines
    visitor.max_class_lines = max_class_lines
    visitor.visit(tree)

    for name, lineno, length in visitor.function_violations:
        violations.append(
            f"{path}:{lineno} function '{name}' length={length} > {max_function_lines}",
        )
    for name, lineno, length in visitor.class_violations:
        violations.append(
            f"{path}:{lineno} class '{name}' length={length} > {max_class_lines}",
        )
    for name, lineno, alias_expr in visitor.alias_violations:
        violations.append(
            f"{path}:{lineno} function '{name}' is a redundant alias ({alias_expr})",
        )

    return violations


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Structural Python quality gates.")
    parser.add_argument(
        "files",
        nargs="*",
        help="Optional list of Python files to scan.",
    )
    parser.add_argument("--max-function-lines", type=int, default=100)
    parser.add_argument("--max-class-lines", type=int, default=500)
    parser.add_argument("--max-file-lines", type=int, default=1000)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    files = [
        path
        for path in _iter_python_files(args.files)
        if path.exists() and not _should_skip(path)
    ]

    if not files:
        print("No Python files to scan.")
        return 0

    violations: list[str] = []
    for path in files:
        violations.extend(
            evaluate_file(
                path,
                max_function_lines=args.max_function_lines,
                max_class_lines=args.max_class_lines,
                max_file_lines=args.max_file_lines,
            ),
        )

    if not violations:
        print("Structural quality gates: OK")
        return 0

    print("::error::Structural quality gate violations detected:")
    for violation in violations:
        print(f" - {violation}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
