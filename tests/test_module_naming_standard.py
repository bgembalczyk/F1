import ast
from pathlib import Path


CANONICAL_MODULE_CLASS_MATRIX = {
    "drivers": {
        "scrapers.drivers_list_scraper": "DriversListScraper",
        "scrapers.drivers_detail_scraper": "DriversDetailScraper",
        "scrapers.drivers_pipeline_service": "DriversPipelineService",
        "scrapers.drivers_factory": "DriversFactory",
    },
    "constructors": {
        "scrapers.constructors_list_scraper": "ConstructorsListScraper",
        "scrapers.constructors_detail_scraper": "ConstructorsDetailScraper",
        "scrapers.constructors_pipeline_service": "ConstructorsPipelineService",
        "scrapers.constructors_factory": "ConstructorsFactory",
    },
    "circuits": {
        "scrapers.circuits_list_scraper": "CircuitsListScraper",
        "scrapers.circuits_detail_scraper": "CircuitsDetailScraper",
        "scrapers.circuits_pipeline_service": "CircuitsPipelineService",
        "scrapers.circuits_factory": "CircuitsFactory",
    },
    "seasons": {
        "scrapers.seasons_list_scraper": "SeasonsListScraper",
        "scrapers.seasons_detail_scraper": "SeasonsDetailScraper",
        "scrapers.seasons_pipeline_service": "SeasonsPipelineService",
        "scrapers.seasons_factory": "SeasonsFactory",
    },
    "grands_prix": {
        "scrapers.grands_prix_list_scraper": "GrandsPrixListScraper",
        "scrapers.grands_prix_detail_scraper": "GrandsPrixDetailScraper",
        "scrapers.grands_prix_pipeline_service": "GrandsPrixPipelineService",
        "scrapers.grands_prix_factory": "GrandsPrixFactory",
    },
}


def test_canonical_module_class_matrix_matches_naming_standard() -> None:
    for _, module_classes in CANONICAL_MODULE_CLASS_MATRIX.items():
        for module_path, class_name in module_classes.items():
            module_file = Path(module_path.replace(".", "/")).with_suffix(".py")
            assert module_file.exists(), f"Missing module file: {module_file}"
            source = module_file.read_text(encoding="utf-8")
            class_names = {
                node.name
                for node in ast.walk(ast.parse(source))
                if isinstance(node, ast.ClassDef)
            }
            assert class_name in class_names, (
                f"Missing '{class_name}' in '{module_path}' ({module_file}). "
                "Keep module/class naming aligned with "
                "docs/architecture/module-naming-standard.md"
            )
