# ruff: noqa: SLF001
from __future__ import annotations

import warnings

from scrapers import cli


def test_run_legacy_wrapper_executes_registered_module(monkeypatch) -> None:
    calls: list[object] = []

    def fake_invoke_target(target, run_config):
        calls.append((target, run_config))

    monkeypatch.setattr(cli, "_invoke_target", fake_invoke_target)
    cli.run_legacy_wrapper("scrapers.drivers.list_scraper", [])

    assert calls


def test_run_legacy_wrapper_does_not_warn_for_new_entrypoint(monkeypatch) -> None:
    calls: list[object] = []

    def fake_invoke_target(target, run_config):
        calls.append((target, run_config))

    monkeypatch.setattr(cli, "_invoke_target", fake_invoke_target)

    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always")
        cli.run_legacy_wrapper("scrapers.drivers.entrypoint", [])

    assert calls
    assert not records


def test_cli_exposes_domain_entrypoints_in_run_choices() -> None:
    parser = cli._build_main_parser()
    run_parser = next(
        action
        for action in parser._actions
        if getattr(action, "dest", None) == "command"
    ).choices["run"]
    choices = next(
        action.choices
        for action in run_parser._actions
        if getattr(action, "dest", None) == "module"
    )

    assert "scrapers.drivers.entrypoint" in choices
    assert "scrapers.circuits.entrypoint" in choices


def test_cli_exposes_domain_registry_choices() -> None:
    parser = cli._build_main_parser()
    domain_parser = next(
        action
        for action in parser._actions
        if getattr(action, "dest", None) == "command"
    ).choices["domain"]
    choices = next(
        action.choices
        for action in domain_parser._actions
        if getattr(action, "dest", None) == "name"
    )
    assert "drivers" in choices
    assert "circuits" in choices
