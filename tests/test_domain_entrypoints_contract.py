from __future__ import annotations

import importlib
import inspect

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


def test_entrypoints_delegate_to_run_and_export_with_default_profile(
    monkeypatch,
) -> None:
    delegate_calls = []

    def fake_run_and_export(
        scraper_cls,
        json_rel,
        csv_rel=None,
        *,
        run_config,
        supports_urls=True,
    ):
        delegate_calls.append(
            {
                "scraper_cls": scraper_cls,
                "json_rel": json_rel,
                "csv_rel": csv_rel,
                "run_config": run_config,
                "supports_urls": supports_urls,
            },
        )

    monkeypatch.setattr(
        "scrapers.base.domain_entrypoint.run_and_export",
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

    def fake_run_and_export(
        scraper_cls,
        json_rel,
        csv_rel=None,
        *,
        run_config,
        supports_urls=True,
    ):
        delegate_calls.append(run_config)

    monkeypatch.setattr(
        "scrapers.base.domain_entrypoint.run_and_export",
        fake_run_and_export,
    )

    custom_config = RunConfig(include_urls=False)
    for module_name in ENTRYPOINT_MODULES:
        module = importlib.import_module(module_name)
        module.run_list_scraper(run_config=custom_config)

    assert delegate_calls == [custom_config] * len(ENTRYPOINT_MODULES)
