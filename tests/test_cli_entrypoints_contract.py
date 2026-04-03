from __future__ import annotations

from importlib import import_module
from pathlib import Path

import pytest

from scrapers.base.cli_entrypoint import complete_extractor_base_config
from scrapers.base.cli_entrypoint import deprecated_module_base_config
from scrapers.base.run_config import RunConfig

IDE_ENTRYPOINT_MODULES = (
    "scrapers.circuits.entrypoint",
    "scrapers.constructors.entrypoint",
    "scrapers.drivers.entrypoint",
    "scrapers.grands_prix.entrypoint",
    "scrapers.seasons.entrypoint",
)

LEGACY_LIST_WRAPPERS = (
    "scrapers/circuits/list_scraper.py",
    "scrapers/constructors/current_constructors_list.py",
    "scrapers/drivers/list_scraper.py",
    "scrapers/grands_prix/list_scraper.py",
    "scrapers/seasons/list_scraper.py",
)


@pytest.mark.parametrize("module_path", IDE_ENTRYPOINT_MODULES)
def test_ide_entrypoints_expose_stable_start_function(module_path: str) -> None:
    module = import_module(module_path)

    assert hasattr(module, "run_list_scraper")
    assert callable(module.run_list_scraper)


@pytest.mark.parametrize("module_path", IDE_ENTRYPOINT_MODULES)
def test_ide_entrypoints_do_not_embed_cli_parsers(module_path: str) -> None:
    source_path = Path(module_path.replace(".", "/") + ".py")
    source = source_path.read_text(encoding="utf-8")

    assert "argparse" not in source
    assert "if __name__ == \"__main__\":" not in source


@pytest.mark.parametrize("file_path", LEGACY_LIST_WRAPPERS)
def test_legacy_list_wrappers_point_to_stable_ide_entrypoint(file_path: str) -> None:
    source = Path(file_path).read_text(encoding="utf-8")

    assert "run_list_scraper" in source
    assert "argparse" not in source


def test_deprecated_module_base_config_has_expected_defaults() -> None:
    assert deprecated_module_base_config() == RunConfig(
        output_dir=Path("../../data/wiki"),
        include_urls=True,
    )


def test_complete_extractor_base_config_has_expected_defaults() -> None:
    assert complete_extractor_base_config() == RunConfig(
        output_dir=Path("../../data/wiki"),
    )
