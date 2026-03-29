from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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

ENTRYPOINT_MODULES: tuple[str, ...] = (
    "scrapers/drivers/entrypoint.py",
    "scrapers/constructors/entrypoint.py",
    "scrapers/circuits/entrypoint.py",
    "scrapers/seasons/entrypoint.py",
    "scrapers/grands_prix/entrypoint.py",
)

LAYERS: tuple[str, ...] = ("list", "sections", "infobox", "postprocess")
MIN_IMPORT_PARTS = 3

REQUIRED_LAYERS_BY_DOMAIN: dict[str, tuple[str, ...]] = {
    "drivers": ("list", "sections", "infobox", "postprocess"),
    "constructors": ("list", "sections", "infobox", "postprocess"),
    "circuits": ("list", "sections", "infobox", "postprocess"),
    "seasons": ("list", "sections", "postprocess"),
    "grands_prix": ("list", "sections"),
}

FORBIDDEN_IMPORTS_BY_LAYER: dict[str, tuple[str, ...]] = {
    "list": ("infobox", "postprocess"),
    "sections": ("list", "single_scraper"),
    "infobox": ("list", "sections", "postprocess", "single_scraper"),
    "postprocess": ("list", "sections", "infobox", "single_scraper"),
}

ALLOWED_IMPORTS_BY_LAYER: dict[str, tuple[str, ...]] = {
    layer: tuple(sorted(set(LAYERS) - {layer} - set(FORBIDDEN_IMPORTS_BY_LAYER[layer])))
    for layer in LAYERS
}


@dataclass(frozen=True)
class ImportDependencyRules:
    allowed: dict[str, tuple[str, ...]]
    forbidden: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class ParsedImport:
    module: str
    level: int


LAYER_DEPENDENCY_RULES = ImportDependencyRules(
    allowed=ALLOWED_IMPORTS_BY_LAYER,
    forbidden=FORBIDDEN_IMPORTS_BY_LAYER,
)


def module_name_for_file(py_file: Path) -> str:
    parts = list(py_file.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def parse_imports(py_file: Path) -> list[ParsedImport]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    imports: list[ParsedImport] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                ParsedImport(module=alias.name, level=0) for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.append(ParsedImport(module=node.module, level=node.level))

    return imports


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


def is_forbidden_single_scraper_import(
    *,
    domain: str,
    imported_module: str | None,
    import_level: int,
) -> bool:
    if imported_module is None:
        return False

    absolute_target = f"scrapers.{domain}.single_scraper"
    relative_target = "single_scraper"

    return imported_module == absolute_target or (
        import_level > 0 and imported_module == relative_target
    )


def collect_single_scraper_import_violations(py_file: Path, domain: str) -> list[str]:
    return [
        f"{'.' * parsed_import.level}{parsed_import.module}"
        for parsed_import in parse_imports(py_file)
        if is_forbidden_single_scraper_import(
            domain=domain,
            imported_module=parsed_import.module,
            import_level=parsed_import.level,
        )
    ]


def collect_cross_domain_import_violations(py_file: Path, domain: str) -> list[str]:
    violations: list[str] = []

    for parsed_import in parse_imports(py_file):
        if parsed_import.level != 0:
            continue
        parts = parsed_import.module.split(".")
        if len(parts) < MIN_IMPORT_PARTS or parts[0] != "scrapers":
            continue
        imported_domain = parts[1]
        if imported_domain in DOMAINS and imported_domain != domain:
            violations.append(parsed_import.module)

    return violations


def infer_layer(py_file: Path, *, domain: str) -> str | None:
    parts = py_file.parts
    if "sections" in parts:
        return "sections"
    if "infobox" in parts:
        return "infobox"
    if "postprocess" in parts:
        return "postprocess"

    filename = py_file.name
    is_named_list_entrypoint = filename in (
        "list_scraper.py",
        "base_constructor_list_scraper.py",
    )
    if is_named_list_entrypoint or filename.endswith(("_list.py", "_list_scraper.py")):
        return "list"

    if f"scrapers/{domain}/" not in py_file.as_posix():
        return None

    return None
