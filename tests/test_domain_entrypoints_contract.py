# ruff: noqa: ARG001
from __future__ import annotations

import importlib
import inspect
import sys
import types
from pathlib import Path

from scrapers.base.domain_entrypoint import get_domain_entrypoint_config
from scrapers.base.run_config import RunConfig

ENTRYPOINT_MODULES = (
    "scrapers.drivers.entrypoint",
    "scrapers.constructors.entrypoint",
    "scrapers.circuits.entrypoint",
    "scrapers.seasons.entrypoint",
    "scrapers.grands_prix.entrypoint",
)


def test_entrypoints_expose_uniform_run_list_scraper_signature() -> None:
    for module_name in ENTRYPOINT_MODULES:
        module = importlib.import_module(module_name)
        signature = inspect.signature(module.run_list_scraper)
        assert str(signature) == "(*, run_config: 'RunConfig | None' = None) -> 'None'"


def test_entrypoints_reuse_centralized_domain_config_registry() -> None:
    for module_name in ENTRYPOINT_MODULES:
        module = importlib.import_module(module_name)
        domain = module_name.split(".")[-2]
        config = get_domain_entrypoint_config(domain)

        assert config == module.ENTRYPOINT_CONFIG
        assert module.LIST_SCRAPER_CLASS is config.list_scraper_cls
        assert config.default_output_json == module.DEFAULT_OUTPUT_JSON
        assert config.default_output_csv == getattr(module, "DEFAULT_OUTPUT_CSV", None)
        assert module.RUN_CONFIG_PROFILE is config.run_config_profile


def test_entrypoints_delegate_to_run_and_export_with_default_profile(
    monkeypatch,
) -> None:
    delegate_calls = []

    def fake_run_and_export(self, scraper_cls, json_rel, csv_rel=None):
        delegate_calls.append(
            {
                "scraper_cls": scraper_cls,
                "json_rel": json_rel,
                "csv_rel": csv_rel,
                "run_config": self._run_config,
            },
        )

    monkeypatch.setattr(
        "scrapers.base.runner.ScraperRunner.run_and_export",
        fake_run_and_export,
    )

    for module_name in ENTRYPOINT_MODULES:
        module = importlib.import_module(module_name)
        module.run_list_scraper()

        assert delegate_calls, f"No delegation call captured for {module_name}"
        call = delegate_calls.pop()

        assert call["scraper_cls"] is module.LIST_SCRAPER_CLASS
        assert call["json_rel"] == module.DEFAULT_OUTPUT_JSON
        assert call["csv_rel"] == getattr(module, "DEFAULT_OUTPUT_CSV", None)
        assert call["run_config"] == module.RUN_CONFIG_PROFILE()


def test_entrypoints_delegate_to_run_and_export_with_overridden_run_config(
    monkeypatch,
) -> None:
    delegate_calls = []

    def fake_run_and_export(self, scraper_cls, json_rel, csv_rel=None):
        delegate_calls.append(self._run_config)

    monkeypatch.setattr(
        "scrapers.base.runner.ScraperRunner.run_and_export",
        fake_run_and_export,
    )

    custom_config = RunConfig(include_urls=False)
    for module_name in ENTRYPOINT_MODULES:
        module = importlib.import_module(module_name)
        module.run_list_scraper(run_config=custom_config)

    assert delegate_calls == [custom_config] * len(ENTRYPOINT_MODULES)


def test_new_domain_requires_only_config_plus_generic_shim(monkeypatch) -> None:
    from scrapers.base import domain_entrypoint as facade

    module_name = "tests.fake_new_domain_entrypoint"
    scraper_module_name = "tests.fake_new_domain_scraper"

    fake_scraper_module = types.ModuleType(scraper_module_name)

    class FakeListScraper:
        pass

    fake_scraper_module.FakeListScraper = FakeListScraper
    sys.modules[scraper_module_name] = fake_scraper_module

    monkeypatch.setitem(
        facade._DOMAIN_ENTRYPOINT_SPECS,
        "new_domain",
        facade._DomainEntrypointSpec(
            scraper_path=f"{scraper_module_name}:FakeListScraper",
            default_output_json="new_domain/fake.json",
            default_output_csv="new_domain/fake.csv",
            run_config_profile=facade.minimal_profile,
        ),
    )
    facade._resolve_domain_entrypoint_config.cache_clear()

    module = types.ModuleType(module_name)
    exec(
        (
            "from scrapers.base.domain_entrypoint import install_domain_entrypoint\n"
            'install_domain_entrypoint(globals(), domain="new_domain")\n'
        ),
        module.__dict__,
    )

    assert callable(module.run_list_scraper)

    config = facade.get_domain_entrypoint_config("new_domain")
    assert module.ENTRYPOINT_CONFIG == config
    assert module.LIST_SCRAPER_CLASS is config.list_scraper_cls
    assert module.DEFAULT_OUTPUT_JSON == config.default_output_json
    assert module.DEFAULT_OUTPUT_CSV == config.default_output_csv
    assert module.RUN_CONFIG_PROFILE is config.run_config_profile
def test_domain_output_path_policy_renders_placeholder_paths() -> None:
    config = get_domain_entrypoint_config("constructors")
    current_year = getattr(
        importlib.import_module("scrapers.constructors.constants"),
        "CURRENT_YEAR",
    )

    assert config.default_output_json == f"constructors/f1_constructors_{current_year}.json"
    assert config.default_output_csv == f"constructors/f1_constructors_{current_year}.csv"


def test_domain_output_path_policy_keeps_non_placeholder_paths() -> None:
    config = get_domain_entrypoint_config("drivers")

    assert config.default_output_json == "drivers/f1_drivers.json"
    assert config.default_output_csv is None


def test_year_placeholder_renderer_handles_path_inputs() -> None:
    from scrapers.base.domain_entrypoint import YearPlaceholderOutputPathRenderer

    rendered = YearPlaceholderOutputPathRenderer(year=2042).render(
        Path("constructors/f1_constructors_{year}.json"),
    )

    assert rendered == Path("constructors/f1_constructors_2042.json")
