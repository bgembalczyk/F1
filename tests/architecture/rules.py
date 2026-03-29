from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from tests.architecture.registry import ARCHITECTURE_REGISTRY

DOMAINS: tuple[str, ...] = ARCHITECTURE_REGISTRY.domain_names
ENTRYPOINT_DOMAINS: tuple[str, ...] = ARCHITECTURE_REGISTRY.entrypoint_domains
LAYERS: tuple[str, ...] = ARCHITECTURE_REGISTRY.layers
REQUIRED_LAYERS_BY_DOMAIN: dict[str, tuple[str, ...]] = (
    ARCHITECTURE_REGISTRY.required_layers_by_domain
)
FORBIDDEN_IMPORTS_BY_LAYER: dict[str, tuple[str, ...]] = (
    ARCHITECTURE_REGISTRY.forbidden_imports_by_layer
)
ALLOWED_IMPORTS_BY_LAYER: dict[str, tuple[str, ...]] = (
    ARCHITECTURE_REGISTRY.allowed_imports_by_layer
)


@dataclass(frozen=True)
class ImportDependencyRules:
    allowed: dict[str, tuple[str, ...]]
    forbidden: dict[str, tuple[str, ...]]


LAYER_DEPENDENCY_RULES = ImportDependencyRules(
    allowed=ALLOWED_IMPORTS_BY_LAYER,
    forbidden=FORBIDDEN_IMPORTS_BY_LAYER,
)


def module_name_for_file(py_file: Path) -> str:
    parts = list(py_file.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def resolve_import_targets(py_file: Path) -> list[str]:
    module_name = module_name_for_file(py_file)
    module_parts = module_name.split(".")
    package_parts = module_parts if py_file.name == "__init__.py" else module_parts[:-1]

    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    targets: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            targets.extend(alias.name for alias in node.names)
            continue

        if not isinstance(node, ast.ImportFrom):
            continue

        if node.level == 0:
            base_parts = []
        else:
            up = node.level - 1
            base_parts = package_parts[:-up] if up else package_parts

        module_parts_from_node = node.module.split(".") if node.module else []
        resolved_base = ".".join([*base_parts, *module_parts_from_node])
        if resolved_base:
            targets.append(resolved_base)

        for alias in node.names:
            if alias.name == "*":
                continue
            if resolved_base:
                targets.append(f"{resolved_base}.{alias.name}")

    return targets


def infer_layer(py_file: Path, *, domain: str) -> str | None:
    parts = py_file.parts
    if "sections" in parts:
        return "sections"
    if "infobox" in parts:
        return "infobox"
    if "postprocess" in parts:
        return "postprocess"

    filename = py_file.name
    if (
        filename == "list_scraper.py"
        or filename.endswith("_list.py")
        or filename.endswith("_list_scraper.py")
        or filename == "base_constructor_list_scraper.py"
    ):
        return "list"

    if f"scrapers/{domain}/" not in py_file.as_posix():
        return None

    return None
