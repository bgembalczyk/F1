# ruff: noqa: SLF001
from __future__ import annotations

import warnings
from pathlib import Path

import pytest

from scrapers import cli


def test_run_legacy_wrapper_warns_for_deprecated_module(monkeypatch) -> None:
    calls: list[object] = []

    def fake_invoke_target(target, run_config):
        calls.append((target, run_config))

    monkeypatch.setattr(cli, "_invoke_target", fake_invoke_target)

    with pytest.warns(DeprecationWarning, match="scheduled for removal after 2"):
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


def test_wiki_parser_supports_deterministic_flag() -> None:
    parser = cli._build_wiki_parser()

    args = parser.parse_args(["--mode", "layer0", "--deterministic"])

    assert args.deterministic is True


def test_get_deprecated_module_migrations_points_to_new_domain_entrypoints() -> None:
    migrations = dict(cli.get_deprecated_module_migrations())

    assert migrations["scrapers.drivers.list_scraper"] == "scrapers.drivers.entrypoint"
    assert (
        migrations["scrapers.circuits.list_scraper"] == "scrapers.circuits.entrypoint"
    )
    assert (
        migrations["scrapers.constructors.current_constructors_list"]
        == "scrapers.constructors.entrypoint"
    )


def test_deprecation_message_has_domain_migration_hint(monkeypatch) -> None:
    def fake_invoke_target(*_args, **_kwargs):
        return None

    monkeypatch.setattr(cli, "_invoke_target", fake_invoke_target)
    with pytest.warns(DeprecationWarning, match="scrapers\\.cli domain drivers"):
        cli.run_legacy_wrapper("scrapers.drivers.list_scraper", [])


def test_runtime_warning_and_docs_schedule_share_same_removal_target() -> None:
    runtime_message = cli._deprecated_runtime_message(
        "scrapers.drivers.list_scraper",
        replacement_module_path="scrapers.drivers.entrypoint",
    )
    docs_schedule = cli.render_deprecation_schedule_markdown()
    docs_path = Path(__file__).resolve().parents[1] / "docs" / "MODULE_BOUNDARIES.md"
    docs_content = docs_path.read_text(encoding="utf-8")

    removal_target = cli.DEPRECATION_POLICY.removal_target
    assert f"removal target: {removal_target}" in runtime_message
    assert f"removal target: {removal_target}" in docs_schedule
    assert docs_schedule in docs_content
