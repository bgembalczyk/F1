# ruff: noqa: ARG001
from __future__ import annotations

import importlib
import inspect
from pathlib import Path

from scrapers.base.domain_entrypoint import get_domain_entrypoint_config
from scrapers.base.domain_entrypoint import get_domain_entrypoint_scraper_metadata
from scrapers.base.run_config import RunConfig


def _entrypoint_modules_from_registry() -> tuple[str, ...]:
    return tuple(
        f"scrapers.{domain}.entrypoint"
        for domain in sorted(get_domain_entrypoint_scraper_metadata())
    )


def _entrypoint_modules_discovered() -> tuple[str, ...]:
    root = Path("scrapers")
    return tuple(
        sorted(
            ".".join(path.with_suffix("").parts)
            for path in root.glob("*/entrypoint.py")
            if path.is_file()
        ),
    )


def test_entrypoints_expose_uniform_run_list_scraper_signature() -> None:
    for module_name in _entrypoint_modules_from_registry():
        module = importlib.import_module(module_name)
        signature = inspect.signature(module.run_list_scraper)
        assert str(signature) == "(*, run_config: 'RunConfig | None' = None) -> 'None'"


def test_entrypoints_reuse_centralized_domain_config_registry() -> None:
    for module_name in _entrypoint_modules_from_registry():
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

    for module_name in _entrypoint_modules_from_registry():
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
    entrypoint_modules = _entrypoint_modules_from_registry()
    for module_name in entrypoint_modules:
        module = importlib.import_module(module_name)
        module.run_list_scraper(run_config=custom_config)

    assert delegate_calls == [custom_config] * len(entrypoint_modules)


def test_entrypoint_registry_matches_discovered_entrypoint_modules() -> None:
    assert _entrypoint_modules_discovered() == _entrypoint_modules_from_registry()
