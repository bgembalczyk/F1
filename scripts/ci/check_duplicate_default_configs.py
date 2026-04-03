from __future__ import annotations

import ast
import json
from pathlib import Path

REGISTRY_PATH = Path("layers/orchestration/runner_registry.py")
TARGET_FUNCTION = "build_layer_zero_run_config_factory_map"


def _ast_to_python_dict(node: ast.Dict) -> dict[str, object] | None:
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError):
        return None


def _extract_static_kwargs_duplicates(tree: ast.AST) -> dict[str, list[str]]:
    duplicates: dict[str, list[str]] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == TARGET_FUNCTION:
            _collect_duplicates_from_target_function(node, duplicates)

    return duplicates


def _collect_duplicates_from_target_function(
    node: ast.FunctionDef,
    duplicates: dict[str, list[str]],
) -> None:
    for statement in node.body:
        if not isinstance(statement, ast.Return) or not isinstance(
            statement.value,
            ast.Dict,
        ):
            continue
        _collect_duplicates_from_return_dict(statement.value, duplicates)


def _collect_duplicates_from_return_dict(
    mapping: ast.Dict,
    duplicates: dict[str, list[str]],
) -> None:
    seen: dict[str, str] = {}
    for key_node, value_node in zip(mapping.keys, mapping.values, strict=False):
        key = _extract_string_key(key_node)
        if key is None:
            continue
        kwargs_value = _extract_scraper_kwargs_dict(value_node)
        if kwargs_value is None:
            continue
        fingerprint = json.dumps(kwargs_value, sort_keys=True, ensure_ascii=True)
        existing = seen.get(fingerprint)
        if existing is None:
            seen[fingerprint] = key
            continue
        duplicates.setdefault(fingerprint, [existing]).append(key)


def _extract_string_key(node: ast.expr | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _extract_scraper_kwargs_dict(call_node: ast.expr) -> dict[str, object] | None:
    if not isinstance(call_node, ast.Call):
        return None
    if not isinstance(call_node.func, ast.Name):
        return None
    if call_node.func.id != "StaticScraperKwargsFactory":
        return None
    for kw in call_node.keywords:
        if kw.arg == "scraper_kwargs" and isinstance(kw.value, ast.Dict):
            return _ast_to_python_dict(kw.value)
    return None


def main() -> int:
    if not REGISTRY_PATH.exists():
        print(f"::error::Brak pliku: {REGISTRY_PATH}")
        return 1

    tree = ast.parse(REGISTRY_PATH.read_text(encoding="utf-8"))
    duplicates = _extract_static_kwargs_duplicates(tree)

    if not duplicates:
        print("Brak duplikatów defaultów konfiguracyjnych: OK")
        return 0

    print("::error::Wykryto duplikaty defaultów konfiguracyjnych (scraper_kwargs):")
    for fingerprint, seeds in duplicates.items():
        print(f" - seeds={seeds} share default={fingerprint}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
