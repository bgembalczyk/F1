from __future__ import annotations

import ast
import json
import sys
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
        if not isinstance(node, ast.FunctionDef) or node.name != TARGET_FUNCTION:
            continue

        for statement in node.body:
            if not isinstance(statement, ast.Return) or not isinstance(statement.value, ast.Dict):
                continue

            seen: dict[str, str] = {}
            for key_node, value_node in zip(statement.value.keys, statement.value.values):
                if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                    continue
                if not isinstance(value_node, ast.Call):
                    continue
                if not isinstance(value_node.func, ast.Name):
                    continue
                if value_node.func.id != "StaticScraperKwargsFactory":
                    continue

                kwargs_value: dict[str, object] | None = None
                for kw in value_node.keywords:
                    if kw.arg == "scraper_kwargs" and isinstance(kw.value, ast.Dict):
                        kwargs_value = _ast_to_python_dict(kw.value)
                        break

                if kwargs_value is None:
                    continue

                fingerprint = json.dumps(kwargs_value, sort_keys=True, ensure_ascii=True)
                existing = seen.get(fingerprint)
                if existing is None:
                    seen[fingerprint] = key_node.value
                    continue

                duplicates.setdefault(fingerprint, [existing]).append(key_node.value)

    return duplicates


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
