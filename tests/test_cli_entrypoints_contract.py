# ruff: noqa: FBT001, SLF001
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from scrapers.base.cli_entrypoint import build_complete_extractor_main
from scrapers.base.cli_entrypoint import build_deprecated_module_main
from scrapers.base.cli_entrypoint import build_standard_parser
from scrapers.base.cli_entrypoint import complete_extractor_base_config
from scrapers.base.cli_entrypoint import deprecated_module_base_config
from scrapers.base.cli_entrypoint import run_cli_entrypoint
from scrapers.base.run_config import RunConfig

if TYPE_CHECKING:
    import argparse

ENTRYPOINT_DEFAULTS = (
    ("scrapers.drivers.list_scraper", True, False),
    ("scrapers.circuits.list_scraper", True, False),
    ("scrapers.grands_prix.list_scraper", False, False),
    ("scrapers.seasons.list_scraper", False, False),
    ("scrapers.constructors.current_constructors_list", False, False),
    ("scrapers.drivers.complete_scraper", False, False),
    ("scrapers.drivers.female_drivers_list", False, False),
    ("scrapers.drivers.fatalities_list_scraper", False, False),
    ("scrapers.circuits.complete_scraper", False, False),
    ("scrapers.grands_prix.complete_scraper", False, False),
    ("scrapers.seasons.complete_scraper", False, False),
    ("scrapers.constructors.complete_scraper", False, False),
    ("scrapers.constructors.former_constructors_list", False, False),
    ("scrapers.constructors.indianapolis_only_constructors_list", False, False),
    ("scrapers.constructors.privateer_teams_list", False, False),
)


def _flags(parser: argparse.ArgumentParser) -> set[str]:
    return {
        option
        for action in parser._actions
        for option in action.option_strings
        if option.startswith("--") and option != "--help"
    }


@pytest.mark.parametrize(
    ("module", "quality_default", "error_default"),
    ENTRYPOINT_DEFAULTS,
)
def test_entrypoint_parsers_expose_consistent_flag_contract(
    module: str,
    quality_default: bool,
    error_default: bool,
) -> None:
    assert module.startswith("scrapers.")
    parser = build_standard_parser(
        quality_report_default=quality_default,
        error_report_default=error_default,
    )

    assert _flags(parser) == {
        "--quality-report",
        "--no-quality-report",
        "--error-report",
        "--no-error-report",
        "--verbose",
        "--trace",
    }

    args = parser.parse_args([])
    assert args.quality_report is quality_default
    assert args.error_report is error_default


def test_cli_runner_passes_run_config_to_run_config_aware_targets() -> None:
    captured: list[RunConfig] = []

    def target(*, run_config: RunConfig) -> None:
        captured.append(run_config)

    run_cli_entrypoint(
        target=target,
        base_config=RunConfig(output_dir=Path("../../data/wiki")),
        argv=["--quality-report", "--error-report"],
    )

    assert captured == [
        RunConfig(
            output_dir=Path("../../data/wiki"),
            quality_report=True,
            error_report=True,
        ),
    ]


def test_cli_runner_supports_targets_without_run_config_argument() -> None:
    called = False

    def target() -> None:
        nonlocal called
        called = True

    run_cli_entrypoint(
        target=target,
        base_config=RunConfig(),
        argv=["--no-quality-report", "--error-report"],
    )

    assert called is True


def test_deprecated_module_base_config_has_expected_defaults() -> None:
    assert deprecated_module_base_config() == RunConfig(
        output_dir=Path("../../data/wiki"),
        include_urls=True,
        debug_dir=Path("../../data/debug"),
    )


def test_complete_extractor_base_config_has_expected_defaults() -> None:
    assert complete_extractor_base_config() == RunConfig(
        output_dir=Path("../../data/wiki"),
    )


def test_build_deprecated_module_main_warns_and_passes_run_config() -> None:
    captured: list[RunConfig] = []

    def target(*, run_config: RunConfig) -> None:
        captured.append(run_config)

    main = build_deprecated_module_main(
        target=target,
        deprecation_message="deprecated module",
        argv=["--error-report"],
    )

    with pytest.warns(DeprecationWarning, match="deprecated module"):
        main()

    assert captured == [
        RunConfig(
            output_dir=Path("../../data/wiki"),
            include_urls=True,
            debug_dir=Path("../../data/debug"),
            quality_report=False,
            error_report=True,
        ),
    ]


def test_build_complete_extractor_main_passes_default_base_config() -> None:
    captured: list[RunConfig] = []

    def target(*, run_config: RunConfig) -> None:
        captured.append(run_config)

    main = build_complete_extractor_main(target=target, argv=["--quality-report"])
    main()

    assert captured == [
        RunConfig(
            output_dir=Path("../../data/wiki"),
            quality_report=True,
            error_report=False,
        ),
    ]
