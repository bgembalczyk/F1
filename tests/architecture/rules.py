from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from layers.types import DomainName
from layers.types import LayerName

DOMAINS: tuple[DomainName, ...] = (
        DomainName.DRIVERS,
    DomainName.CONSTRUCTORS,
    DomainName.CIRCUITS,
    DomainName.SEASONS,
    DomainName.GRANDS_PRIX,
    DomainName.ENGINES,
    DomainName.POINTS,
    DomainName.SPONSORSHIP_LIVERIES,
    DomainName.TYRES,
)

ENTRYPOINT_DOMAINS: tuple[DomainName, ...] = (
    DomainName.DRIVERS,
    DomainName.CONSTRUCTORS,
    DomainName.CIRCUITS,
    DomainName.SEASONS,
    DomainName.GRANDS_PRIX,
)

LAYERS: tuple[LayerName, ...] = (
    LayerName.LIST,
    LayerName.SECTIONS,
    LayerName.INFOBOX,
    LayerName.POSTPROCESS,
)

REQUIRED_LAYERS_BY_DOMAIN: dict[DomainName, tuple[LayerName, ...]] = {
    DomainName.DRIVERS: (LayerName.LIST, LayerName.SECTIONS, LayerName.INFOBOX, LayerName.POSTPROCESS),
    DomainName.CONSTRUCTORS: (LayerName.LIST, LayerName.SECTIONS, LayerName.INFOBOX, LayerName.POSTPROCESS),
    DomainName.CIRCUITS: (LayerName.LIST, LayerName.SECTIONS, LayerName.INFOBOX, LayerName.POSTPROCESS),
    DomainName.SEASONS: (LayerName.LIST, LayerName.SECTIONS, LayerName.POSTPROCESS),
    DomainName.GRANDS_PRIX: (LayerName.LIST, LayerName.SECTIONS),
}

FORBIDDEN_IMPORTS_BY_LAYER: dict[LayerName, tuple[str, ...]] = {
    LayerName.LIST: ("infobox", "postprocess"),
    LayerName.SECTIONS: ("list", "single_scraper"),
    LayerName.INFOBOX: ("list", "sections", "postprocess", "single_scraper"),
    LayerName.POSTPROCESS: ("list", "sections", "infobox", "single_scraper"),
}

ALLOWED_IMPORTS_BY_LAYER: dict[LayerName, tuple[str, ...]] = {
    layer: tuple(
        sorted(
            (
                allowed.value
                for allowed in set(LAYERS) - {layer}
                if allowed.value not in FORBIDDEN_IMPORTS_BY_LAYER[layer]
            ),
        ),
    )
    for layer in LAYERS
}


@dataclass(frozen=True)
class ImportDependencyRules:
    allowed: dict[LayerName, tuple[str, ...]]
    forbidden: dict[LayerName, tuple[str, ...]]


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


def infer_layer(py_file: Path, *, domain: DomainName) -> LayerName | None:
    parts = py_file.parts
    if "sections" in parts:
        return LayerName.SECTIONS
    if "infobox" in parts:
        return LayerName.INFOBOX
    if "postprocess" in parts:
        return LayerName.POSTPROCESS

    filename = py_file.name
    if (
        filename == "list_scraper.py"
        or filename.endswith("_list.py")
        or filename.endswith("_list_scraper.py")
        or filename == "base_constructor_list_scraper.py"
    ):
        return LayerName.LIST

    if f"scrapers/{domain}/" not in py_file.as_posix():
        return None

    return None
