from __future__ import annotations

import argparse
import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from scripts.ci.git_diff import build_added_lines_map
from scripts.ci.git_diff import list_changed_files
from scripts.ci.quality_gate_constants import CRITICAL_DEFAULT_LITERALS
from scripts.ci.quality_gate_constants import JUSTIFIED_EXCEPTION_MARKER

if TYPE_CHECKING:
    from collections.abc import Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
SEED_REGISTRY_FILE = REPO_ROOT / "layers/seed/registry/constants.py"
RUNNER_REGISTRY_FILE = REPO_ROOT / "layers/orchestration/runner_registry.py"
CENTRAL_DEFAULTS_FILE = REPO_ROOT / "scripts/ci/quality_gate_constants.py"


@dataclass(frozen=True)
class Violation:
    path: str
    line: int
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Gate dla nowych zmian: printy, magic-string/defaults, jawnie uzasadnione "
            "except Exception oraz spójność registry konfiguracji z implementacją."
        ),
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    return parser.parse_args(argv)


def _iter_added_python_lines(
    added_lines_map: dict[str, set[int]],
) -> list[tuple[str, int, str]]:
    records: list[tuple[str, int, str]] = []
    for rel_path, line_numbers in sorted(added_lines_map.items()):
        if not rel_path.endswith(".py"):
            continue
        file_path = REPO_ROOT / rel_path
        if not file_path.exists():
            continue
        lines = file_path.read_text(encoding="utf-8").splitlines()
        records.extend(
            (rel_path, line_no, lines[line_no - 1])
            for line_no in sorted(line_numbers)
            if 1 <= line_no <= len(lines)
        )
    return records


def _check_new_prints(added_lines_map: dict[str, set[int]]) -> list[Violation]:
    violations: list[Violation] = []
    for rel_path, line_no, line in _iter_added_python_lines(added_lines_map):
        stripped = line.strip()
        if stripped.startswith("print("):
            violations.append(
                Violation(
                    path=rel_path,
                    line=line_no,
                    message="Nowy print() jest zablokowany (użyj loggera).",
                ),
            )
    return violations


def _check_critical_defaults_duplication(
    added_lines_map: dict[str, set[int]],
) -> list[Violation]:
    violations: list[Violation] = []
    for rel_path, line_no, line in _iter_added_python_lines(added_lines_map):
        if (REPO_ROOT / rel_path).resolve() == CENTRAL_DEFAULTS_FILE.resolve():
            continue
        lowered = line.lower()
        for literal in CRITICAL_DEFAULT_LITERALS:
            if f'"{literal}"' in lowered or f"'{literal}'" in lowered:
                violations.append(
                    Violation(
                        path=rel_path,
                        line=line_no,
                        message=(
                            "Duplikacja krytycznego defaultu; użyj stałej z "
                            "scripts/ci/quality_gate_constants.py."
                        ),
                    ),
                )
                break
    return violations


def _check_broad_exceptions_with_justification(
    added_lines_map: dict[str, set[int]],
) -> list[Violation]:
    violations: list[Violation] = []
    for rel_path, source, tree, added_set in _iter_python_asts(added_lines_map):
        source_lines = source.splitlines()
        for node in ast.walk(tree):
            if not _is_unjustified_broad_exception(node, added_set, source_lines):
                continue
            violations.append(
                Violation(
                    path=rel_path,
                    line=node.lineno,
                    message=(
                        "except Exception wymaga adnotacji 'justified-exception:' z "
                        "uzasadnieniem."
                    ),
                ),
            )
    return violations


def _extract_string_tuple_assignment(path: Path, symbol: str) -> tuple[str, ...]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        tuple_node = _extract_target_tuple(node, symbol)
        if tuple_node is not None:
            return _tuple_string_values(tuple_node)
    return ()


def _iter_python_asts(
    added_lines_map: dict[str, set[int]],
) -> list[tuple[str, str, ast.AST, set[int]]]:
    records: list[tuple[str, str, ast.AST, set[int]]] = []
    for rel_path, line_numbers in sorted(added_lines_map.items()):
        if not rel_path.endswith(".py"):
            continue
        file_path = REPO_ROOT / rel_path
        if not file_path.exists():
            continue
        source = file_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        records.append((rel_path, source, tree, set(line_numbers)))
    return records


def _is_unjustified_broad_exception(
    node: ast.AST,
    added_set: set[int],
    source_lines: list[str],
) -> bool:
    if not isinstance(node, ast.ExceptHandler):
        return False
    if node.lineno not in added_set:
        return False
    if not isinstance(node.type, ast.Name) or node.type.id != "Exception":
        return False
    handler_line = source_lines[node.lineno - 1].lower()
    return JUSTIFIED_EXCEPTION_MARKER not in handler_line


def _extract_target_tuple(node: ast.stmt, symbol: str) -> ast.Tuple | None:
    if isinstance(node, ast.Assign):
        if len(node.targets) != 1:
            return None
        target = node.targets[0]
        if isinstance(target, ast.Name) and target.id == symbol and isinstance(
            node.value,
            ast.Tuple,
        ):
            return node.value
        return None
    if isinstance(node, ast.AnnAssign):
        if (
            isinstance(node.target, ast.Name)
            and node.target.id == symbol
            and isinstance(node.value, ast.Tuple)
        ):
            return node.value
    return None


def _tuple_string_values(tuple_node: ast.Tuple) -> tuple[str, ...]:
    values = [
        elt.value
        for elt in tuple_node.elts
        if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
    ]
    return tuple(values)


def _extract_runner_map_keys(path: Path, function_name: str) -> tuple[str, ...]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or node.name != function_name:
            continue
        for stmt in node.body:
            if not isinstance(stmt, ast.Return):
                continue
            if not isinstance(stmt.value, ast.Dict):
                continue
            keys = [
                key_node.value
                for key_node in stmt.value.keys
                if isinstance(key_node, ast.Constant)
                and isinstance(key_node.value, str)
            ]
            return tuple(keys)
    return ()


def _check_registry_implementation_drift() -> list[Violation]:
    registry_order = set(
        _extract_string_tuple_assignment(
            SEED_REGISTRY_FILE,
            "_LAYER_ONE_SEED_REGISTRY_ORDER",
        ),
    )
    explicit_runner_keys = set(
        _extract_runner_map_keys(
            RUNNER_REGISTRY_FILE,
            "_build_explicit_layer_one_runner_map",
        ),
    )

    if not registry_order or not explicit_runner_keys:
        return [
            Violation(
                path="layers/seed/registry/constants.py",
                line=1,
                message="Nie udało się sparsować rejestrów do walidacji spójności.",
            ),
        ]

    violations: list[Violation] = []
    missing_in_runners = sorted(registry_order - explicit_runner_keys)
    missing_in_registry = sorted(explicit_runner_keys - registry_order)

    violations.extend(
        Violation(
            path="layers/orchestration/runner_registry.py",
            line=1,
            message=(
                f"Seed '{seed}' jest w rejestrze, ale brak go "
                "w explicit runner map."
            ),
        )
        for seed in missing_in_runners
    )
    violations.extend(
        Violation(
            path="layers/seed/registry/constants.py",
            line=1,
            message=(
                f"Seed '{seed}' jest w explicit runner map, "
                "ale brak go w seed registry."
            ),
        )
        for seed in missing_in_registry
    )
    return violations


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    changed_files = list_changed_files(args.base_sha, args.head_sha)
    added_lines_map = build_added_lines_map(args.base_sha, args.head_sha, changed_files)

    violations = [
        *_check_new_prints(added_lines_map),
        *_check_critical_defaults_duplication(added_lines_map),
        *_check_broad_exceptions_with_justification(added_lines_map),
        *_check_registry_implementation_drift(),
    ]

    if violations:
        print("Diff quality guards: FAILED")
        for violation in violations:
            print(f" - {violation.format()}")
        return 1

    print("Diff quality guards: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
