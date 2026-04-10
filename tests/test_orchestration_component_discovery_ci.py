from __future__ import annotations

import ast
from pathlib import Path


def _iter_orchestration_paths() -> tuple[Path, ...]:
    root = Path(__file__).resolve().parents[1]
    module_paths = set(root.glob("layers/runners/layer_job/*.py"))
    module_paths.update(root.glob("layers/zero/run_config_factories/*.py"))
    paths: list[Path] = []
    for path in module_paths:
        if path.stem == "__init__":
            continue
        paths.append(path)
    return tuple(sorted(paths))


def _is_component_class(node: ast.ClassDef) -> bool:
    valid_bases = {"LayerJobRunner", "LayerZeroRunConfigFactory"}
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id in valid_bases:
            return True
    return False


def _has_required_constructor_args(node: ast.ClassDef) -> bool:
    for item in node.body:
        if not isinstance(item, ast.FunctionDef):
            continue
        if item.name != "__init__":
            continue
        args = item.args.args[1:]  # skip self
        defaults_offset = len(args) - len(item.args.defaults)
        for idx, arg in enumerate(args):
            if arg.arg in {"args", "kwargs"}:
                continue
            if idx < defaults_offset:
                return True
        for kw_arg, default in zip(item.args.kwonlyargs, item.args.kw_defaults):
            if kw_arg.arg in {"args", "kwargs"}:
                continue
            if default is None:
                return True
        return False
    return False


def test_ci_orchestration_components_are_discoverable() -> None:
    not_discoverable: list[str] = []
    for path in _iter_orchestration_paths():
        module = ast.parse(path.read_text(encoding="utf-8"))
        for node in module.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if not _is_component_class(node):
                continue
            if _has_required_constructor_args(node):
                continue
            attrs = {
                stmt.targets[0].id
                for stmt in node.body
                if isinstance(stmt, ast.Assign)
                and len(stmt.targets) == 1
                and isinstance(stmt.targets[0], ast.Name)
            }
            if {"role", "domain", "stage"}.issubset(attrs):
                continue
            not_discoverable.append(f"{path}:{node.name}")

    assert not not_discoverable, (
        "Found orchestration components that cannot be auto-discovered: "
        f"{', '.join(sorted(not_discoverable))}"
    )
