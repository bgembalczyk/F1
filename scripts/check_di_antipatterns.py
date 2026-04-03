#!/usr/bin/env python3
from __future__ import annotations

import ast
import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

_BOOTSTRAP_PATH = Path(__file__).resolve().parent / "lib" / "bootstrap.py"
_BOOTSTRAP_SPEC = importlib.util.spec_from_file_location(
    "_scripts_bootstrap",
    _BOOTSTRAP_PATH,
)
assert _BOOTSTRAP_SPEC
assert _BOOTSTRAP_SPEC.loader
_BOOTSTRAP_MODULE = importlib.util.module_from_spec(_BOOTSTRAP_SPEC)
_BOOTSTRAP_SPEC.loader.exec_module(_BOOTSTRAP_MODULE)

REPO_ROOT = _BOOTSTRAP_MODULE.ensure_repo_root_on_sys_path()

from scripts.ci.adr_enforcement_policy import DEFAULT_ADR_ENFORCEMENT_POLICY
from scripts.lib.check_runner import iter_python_paths
from scripts.lib.check_runner import run_cli

DEFAULT_TARGETS = [REPO_ROOT / "layers", REPO_ROOT / "scrapers" / "base"]

DI_SUSPECT_SUFFIXES = (
    "Client",
    "Service",
    "Repository",
    "Adapter",
    "Fetcher",
    "Parser",
    "Collector",
    "Provider",
    "Discovery",
    "Chain",
)
ALLOWED_FACTORY_METHOD_PATTERNS = (
    "__init__",
    "build",
    "builder",
    "factory",
    "create",
    "compose",
    "wire",
    "bootstrap",
    "setup",
    "configure",
)
ALLOW_COMMENT = "di-antipattern-allow:"
DI_ADR_THRESHOLD = 5


@dataclass(frozen=True)
class Violation:
    path: Path
    lineno: int
    method_name: str
    class_name: str
    dependency_name: str
    violation_type: str = "creation"

    def format_message(self, repo_root: Path) -> str:
        rel = self.path.relative_to(repo_root)
        if self.violation_type == "import":
            return (
                f"{rel}:{self.lineno} {self.class_name}.{self.method_name} -> "
                f"ukryty import '{self.dependency_name}' wewnątrz metody biznesowej. "
                "Sugerowane: przenieś import do modułu lub wstrzyknij "
                "zależność przez __init__/factory (DI)."
            )
        return (
            f"{rel}:{self.lineno} {self.class_name}.{self.method_name} -> "
            f"utworzono '{self.dependency_name}' wewnątrz metody biznesowej. "
            "Sugerowane: wstrzyknij zależność przez __init__/factory (DI)."
        )


class DependencyCreationVisitor(ast.NodeVisitor):
    def __init__(self, source_lines: list[str], path: Path) -> None:
        self.source_lines = source_lines
        self.path = path
        self.violations: list[Violation] = []
        self._class_stack: list[str] = []
        self._method_stack: list[str] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:  # noqa: N802
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:  # noqa: N802
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:  # noqa: N802
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._method_stack.append(node.name)
        self.generic_visit(node)
        self._method_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        class_name = self._class_stack[-1] if self._class_stack else "<module>"
        method_name = self._method_stack[-1] if self._method_stack else "<module>"

        dependency_name = _called_name(node.func)
        if (
            dependency_name
            and _looks_like_dependency_creation(dependency_name)
            and _is_business_method(method_name)
            and not _has_allow_comment(self.source_lines, node.lineno)
        ):
            self.violations.append(
                Violation(
                    path=self.path,
                    lineno=node.lineno,
                    method_name=method_name,
                    class_name=class_name,
                    dependency_name=dependency_name,
                ),
            )
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        if not self._is_hidden_import(node.lineno):
            return
        dependency_name = ", ".join(alias.name for alias in node.names)
        class_name = self._class_stack[-1] if self._class_stack else "<module>"
        method_name = self._method_stack[-1] if self._method_stack else "<module>"
        self.violations.append(
            Violation(
                path=self.path,
                lineno=node.lineno,
                method_name=method_name,
                class_name=class_name,
                dependency_name=dependency_name,
                violation_type="import",
            ),
        )

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        if not self._is_hidden_import(node.lineno):
            return
        names = ", ".join(alias.name for alias in node.names)
        module = node.module or ""
        dependency_name = f"{module}:{names}" if module else names
        class_name = self._class_stack[-1] if self._class_stack else "<module>"
        method_name = self._method_stack[-1] if self._method_stack else "<module>"
        self.violations.append(
            Violation(
                path=self.path,
                lineno=node.lineno,
                method_name=method_name,
                class_name=class_name,
                dependency_name=dependency_name,
                violation_type="import",
            ),
        )

    def _is_hidden_import(self, lineno: int) -> bool:
        if not self._method_stack:
            return False
        method_name = self._method_stack[-1]
        return _is_business_method(method_name) and not _has_allow_comment(
            self.source_lines,
            lineno,
        )


def _called_name(func: ast.expr) -> str | None:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


def _looks_like_dependency_creation(called_name: str) -> bool:
    if called_name.lower() == called_name:
        return False
    return any(called_name.endswith(suffix) for suffix in DI_SUSPECT_SUFFIXES)


def _is_business_method(method_name: str) -> bool:
    lowered = method_name.lower()
    return not any(pattern in lowered for pattern in ALLOWED_FACTORY_METHOD_PATTERNS)


def _has_allow_comment(source_lines: list[str], lineno: int) -> bool:
    start = max(0, lineno - 3)
    return any(ALLOW_COMMENT in line for line in source_lines[start:lineno])


def lint_path(path: Path) -> list[Violation]:
    source = path.read_text(encoding="utf-8")
    source_lines = source.splitlines()
    tree = ast.parse(source, filename=str(path))
    visitor = DependencyCreationVisitor(source_lines=source_lines, path=path)
    visitor.visit(tree)
    return visitor.violations


def run_check(paths: list[Path] | None = None) -> list[Violation]:
    targets = paths or DEFAULT_TARGETS
    violations: list[Violation] = []
    for path in iter_python_paths(targets):
        violations.extend(lint_path(path))
    return violations


def run_check_messages(paths: list[Path] | None = None) -> list[str]:
    return [v.format_message(REPO_ROOT) for v in run_check(paths)]


def _validate_adr_reference_for_major_changes(
    violations: list[Violation],
    adr_reference_text: str,
    threshold: int,
) -> list[str]:
    if not DEFAULT_ADR_ENFORCEMENT_POLICY.should_emit_di_trigger_signal(
        len(violations),
        threshold,
    ):
        return []
    if DEFAULT_ADR_ENFORCEMENT_POLICY.has_adr_reference(adr_reference_text):
        return []
    return [
        (
            f"Wykryto {len(violations)} naruszeń DI (>= {threshold}); "
            "to dodatkowy sygnał DI-trigger i wymagane jest "
            "odniesienie ADR-XXXX w PR/commit message."
        ),
    ]


def main(argv: list[str] | None = None) -> int:
    argv = argv or []
    paths: list[Path] = []
    adr_reference_text = ""
    adr_required_violation_threshold = (
        DEFAULT_ADR_ENFORCEMENT_POLICY.di_required_violation_threshold
    )

    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--adr-reference-text" and i + 1 < len(argv):
            adr_reference_text = argv[i + 1]
            i += 2
            continue
        if arg == "--adr-required-violation-threshold" and i + 1 < len(argv):
            adr_required_violation_threshold = int(argv[i + 1])
            i += 2
            continue
        paths.append(Path(arg))
        i += 1

    resolved_paths = [REPO_ROOT / path for path in paths] if paths else None

    def _runner() -> list[str]:
        violations = run_check(resolved_paths)
        messages = [v.format_message(REPO_ROOT) for v in violations]
        messages.extend(
            _validate_adr_reference_for_major_changes(
                violations=violations,
                adr_reference_text=adr_reference_text,
                threshold=adr_required_violation_threshold,
            ),
        )
        return messages

    return run_cli("di-antipatterns", _runner)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
