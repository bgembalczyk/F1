from __future__ import annotations

import ast
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
@dataclass(frozen=True)
class ArchitectureDomainSpec:
    domain: str
    has_entrypoint: bool
    required_layers: tuple[str, ...] = ()
    entrypoint_scraper_path: str | None = None
    entrypoint_output_json: str | Path | None = None
    entrypoint_output_csv: str | Path | None = None
    entrypoint_run_profile: str | None = None
    layer_one_runner_path: str | None = None
    layer_one_export_function_path: str | None = None


LAYERS: tuple[str, ...] = ("list", "sections", "infobox", "postprocess")

ARCHITECTURE_DOMAINS: tuple[ArchitectureDomainSpec, ...] = (
    ArchitectureDomainSpec(
        domain="drivers",
        has_entrypoint=True,
        required_layers=("list", "sections", "infobox", "postprocess"),
        entrypoint_scraper_path="scrapers.drivers.list_scraper:F1DriversListScraper",
        entrypoint_output_json="drivers/f1_drivers.json",
        entrypoint_run_profile="strict_quality",
        layer_one_export_function_path="scrapers.drivers.helpers.export:export_complete_drivers",
    ),
    ArchitectureDomainSpec(
        domain="constructors",
        has_entrypoint=True,
        required_layers=("list", "sections", "infobox", "postprocess"),
        entrypoint_scraper_path=(
            "scrapers.constructors.current_constructors_list:CurrentConstructorsListScraper"
        ),
        entrypoint_output_json="constructors/f1_constructors_{year}.json",
        entrypoint_output_csv="constructors/f1_constructors_{year}.csv",
        entrypoint_run_profile="minimal_debug",
        layer_one_export_function_path=(
            "scrapers.constructors.helpers.export:export_complete_constructors"
        ),
    ),
    ArchitectureDomainSpec(
        domain="circuits",
        has_entrypoint=True,
        required_layers=("list", "sections", "infobox", "postprocess"),
        entrypoint_scraper_path="scrapers.circuits.list_scraper:CircuitsListScraper",
        entrypoint_output_json="circuits/f1_circuits.json",
        entrypoint_output_csv="circuits/f1_circuits.csv",
        entrypoint_run_profile="strict_quality",
        layer_one_export_function_path="scrapers.circuits.helpers.export:export_complete_circuits",
    ),
    ArchitectureDomainSpec(
        domain="seasons",
        has_entrypoint=True,
        required_layers=("list", "sections", "postprocess"),
        entrypoint_scraper_path="scrapers.seasons.list_scraper:SeasonsListScraper",
        entrypoint_output_json="seasons/f1_seasons.json",
        entrypoint_output_csv="seasons/f1_seasons.csv",
        entrypoint_run_profile="minimal",
        layer_one_export_function_path="scrapers.seasons.helpers:export_complete_seasons",
    ),
    ArchitectureDomainSpec(
        domain="grands_prix",
        has_entrypoint=True,
        required_layers=("list", "sections"),
        entrypoint_scraper_path="scrapers.grands_prix.list_scraper:GrandsPrixListScraper",
        entrypoint_output_json="grands_prix/f1_grands_prix_by_title.json",
        entrypoint_output_csv="grands_prix/f1_grands_prix_by_title.csv",
        entrypoint_run_profile="minimal",
        layer_one_runner_path="layers.orchestration.runners.grand_prix:GrandPrixRunner",
    ),
    ArchitectureDomainSpec(domain="engines", has_entrypoint=False),
    ArchitectureDomainSpec(domain="points", has_entrypoint=False),
    ArchitectureDomainSpec(
        domain="sponsorship_liveries",
        has_entrypoint=False,
    ),
    ArchitectureDomainSpec(domain="tyres", has_entrypoint=False),
)

DOMAIN_SPEC_BY_NAME: dict[str, ArchitectureDomainSpec] = {
    spec.domain: spec for spec in ARCHITECTURE_DOMAINS
}

DOMAINS: tuple[str, ...] = tuple(spec.domain for spec in ARCHITECTURE_DOMAINS)
ENTRYPOINT_DOMAINS: tuple[str, ...] = tuple(
    spec.domain for spec in ARCHITECTURE_DOMAINS if spec.has_entrypoint
)
REQUIRED_LAYERS_BY_DOMAIN: dict[str, tuple[str, ...]] = {
    spec.domain: spec.required_layers
    for spec in ARCHITECTURE_DOMAINS
    if spec.required_layers
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


def _import_target(path: str) -> object:
    module_name, attr_name = path.split(":", maxsplit=1)
    module = import_module(module_name)
    return getattr(module, attr_name)


def _iter_layer_files(domain_dir: Path, domain: str) -> list[tuple[Path, str]]:
    collected: list[tuple[Path, str]] = []
    for py_file in domain_dir.rglob("*.py"):
        layer = infer_layer(py_file, domain=domain)
        if layer in LAYERS:
            collected.append((py_file, layer))
    return collected


def validate_architecture_registry(*, root: Path | None = None) -> tuple[str, ...]:
    repo_root = root or Path(".")
    scrapers_root = repo_root / "scrapers"
    layers_root = repo_root / "layers"
    errors: list[str] = []

    for spec in ARCHITECTURE_DOMAINS:
        domain_dir = scrapers_root / spec.domain
        if not domain_dir.is_dir():
            errors.append(f"missing domain directory: {domain_dir}")
            continue

        has_entrypoint_file = (domain_dir / "entrypoint.py").exists()
        if has_entrypoint_file != spec.has_entrypoint:
            errors.append(
                f"{spec.domain}: has_entrypoint={spec.has_entrypoint} but file_exists={has_entrypoint_file}"
            )

        if spec.required_layers:
            available_layers = {layer for _, layer in _iter_layer_files(domain_dir, spec.domain)}
            missing_layers = set(spec.required_layers) - available_layers
            if missing_layers:
                errors.append(
                    f"{spec.domain}: missing required layers {sorted(missing_layers)}"
                )

        if spec.has_entrypoint:
            if spec.entrypoint_scraper_path is None:
                errors.append(f"{spec.domain}: missing entrypoint_scraper_path")
            if spec.entrypoint_output_json is None:
                errors.append(f"{spec.domain}: missing entrypoint_output_json")
            if spec.entrypoint_run_profile is None:
                errors.append(f"{spec.domain}: missing entrypoint_run_profile")

        if spec.entrypoint_scraper_path is not None:
            try:
                _import_target(spec.entrypoint_scraper_path)
            except (ImportError, AttributeError) as exc:
                errors.append(
                    f"{spec.domain}: cannot import entrypoint scraper {spec.entrypoint_scraper_path} ({exc})"
                )

        if spec.layer_one_runner_path is not None:
            try:
                _import_target(spec.layer_one_runner_path)
            except (ImportError, AttributeError) as exc:
                errors.append(
                    f"{spec.domain}: cannot import layer-one runner {spec.layer_one_runner_path} ({exc})"
                )

        if spec.layer_one_export_function_path is not None:
            try:
                _import_target(spec.layer_one_export_function_path)
            except (ImportError, AttributeError) as exc:
                errors.append(
                    f"{spec.domain}: cannot import layer-one export function {spec.layer_one_export_function_path} ({exc})"
                )

    discovered_domains = {
        path.name
        for path in scrapers_root.iterdir()
        if path.is_dir() and path.name not in {"base", "wiki", "__pycache__"}
    }
    if discovered_domains != set(DOMAINS):
        errors.append(
            "registry domains mismatch discovered packages: "
            f"discovered={sorted(discovered_domains)} configured={sorted(DOMAINS)}"
        )

    discovered_entrypoint_domains = {
        path.name
        for path in scrapers_root.iterdir()
        if path.is_dir() and (path / "entrypoint.py").exists()
    }
    if discovered_entrypoint_domains != set(ENTRYPOINT_DOMAINS):
        errors.append(
            "registry entrypoint domains mismatch: "
            f"discovered={sorted(discovered_entrypoint_domains)} configured={sorted(ENTRYPOINT_DOMAINS)}"
        )

    if not layers_root.exists():
        errors.append(f"missing layers root: {layers_root}")

    return tuple(errors)


def validate_architecture_registry_or_raise(*, root: Path | None = None) -> None:
    errors = validate_architecture_registry(root=root)
    if errors:
        joined = "\n".join(f"- {message}" for message in errors)
        raise ValueError(f"Architecture registry validation failed:\n{joined}")


def get_entrypoint_domain_specs() -> tuple[ArchitectureDomainSpec, ...]:
    return tuple(spec for spec in ARCHITECTURE_DOMAINS if spec.has_entrypoint)


def get_layer_one_runner_specs() -> tuple[ArchitectureDomainSpec, ...]:
    return tuple(
        spec
        for spec in ARCHITECTURE_DOMAINS
        if spec.layer_one_runner_path is not None
        or spec.layer_one_export_function_path is not None
    )
