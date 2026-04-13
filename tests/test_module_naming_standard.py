import ast
from pathlib import Path

CANONICAL_MODULE_CLASS_MATRIX = {
    "drivers": {
        "scrapers.drivers.list_scraper": "DriversListScraper",
        "scrapers.drivers.single_scraper": "DriversDetailScraper",
        "scrapers.drivers_pipeline_service": "DriversPipelineService",
        "scrapers.drivers_factory": "DriverScraperCompositionFactory",
    },
    "constructors": {
        "scrapers.constructors.list_scraper": "ConstructorsListScraper",
        "scrapers.constructors.single_scraper": "ConstructorsDetailScraper",
        "scrapers.constructors_pipeline_service": "ConstructorsPipelineService",
        "scrapers.constructors_factory": "ConstructorsFactory",
    },
    "circuits": {
        "scrapers.circuits.list_scraper": "CircuitsListScraper",
        "scrapers.circuits_pipeline_service": "CircuitsPipelineService",
        "scrapers.circuits_factory": "CircuitsFactory",
    },
    "seasons": {
        "scrapers.seasons.list_scraper": "SeasonsListScraper",
        "scrapers.seasons.single_scraper": "SeasonsDetailScraper",
        "scrapers.seasons_pipeline_service": "SeasonsPipelineService",
        "scrapers.seasons_factory": "SeasonsFactory",
    },
    "grands_prix": {
        "scrapers.grands_prix.list_scraper": "GrandsPrixListScraper",
        "scrapers.grands_prix.single_scraper": "GrandsPrixDetailScraper",
        "scrapers.grands_prix_pipeline_service": "GrandsPrixPipelineService",
        "scrapers.grands_prix_factory": "GrandsPrixFactory",
    },
}


def _extract_all_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if any(
            not isinstance(target, ast.Name) or target.id != "__all__"
            for target in node.targets
        ):
            continue
        if isinstance(node.value, (ast.List, ast.Tuple)):
            for element in node.value.elts:
                if isinstance(element, ast.Constant) and isinstance(element.value, str):
                    names.add(element.value)
    return names


def _extract_exported_symbols(tree: ast.AST) -> set[str]:
    exported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            exported.add(node.name)
        elif isinstance(node, ast.ImportFrom):
            for imported in node.names:
                exported.add(imported.asname or imported.name)
    return exported


def test_canonical_module_class_matrix_matches_naming_standard() -> None:
    for _, module_classes in CANONICAL_MODULE_CLASS_MATRIX.items():
        for module_path, class_name in module_classes.items():
            module_file = Path(module_path.replace(".", "/")).with_suffix(".py")
            assert module_file.exists(), f"Missing module file: {module_file}"
            source = module_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
            exported_symbols = _extract_exported_symbols(tree)
            assert class_name in exported_symbols, (
                f"Missing '{class_name}' in '{module_path}' ({module_file}). "
                "Keep module/class naming aligned with "
                "docs/architecture/module-naming-standard.md"
            )
            all_names = _extract_all_names(tree)
            assert (
                class_name in all_names
            ), f"'{class_name}' should be exported from '{module_path}' via __all__."
