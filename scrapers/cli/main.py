from __future__ import annotations

import argparse
from pathlib import Path

from scrapers.cli.dispatch import run_registered_module
from scrapers.cli.legacy_registry import DOMAIN_COMMANDS
from scrapers.cli.legacy_registry import MODULE_DEFINITIONS


def _build_main_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Canonical scraper CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("module", choices=tuple(sorted(MODULE_DEFINITIONS)))

    domain_parser = subparsers.add_parser("domain")
    domain_parser.add_argument("name", choices=tuple(sorted(DOMAIN_COMMANDS)))

    wiki_parser = subparsers.add_parser("wiki")
    wiki_parser.add_argument(
        "--mode",
        choices=("layer0", "layer1", "full"),
        default="layer0",
    )

    subparsers.add_parser("list-commands")

    return parser


def _build_wiki_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Canonical wiki pipeline launcher")
    parser.add_argument(
        "--mode",
        choices=("layer0", "layer1", "full"),
        default="layer0",
    )
    return parser


def run_wiki_cli(argv: list[str] | None = None) -> None:
    parser = _build_wiki_parser()
    args = parser.parse_args(argv)

    from layers.application import create_default_wiki_pipeline_application

    app = create_default_wiki_pipeline_application(
        base_wiki_dir=Path("data/wiki").resolve(),
        base_debug_dir=Path("data/debug").resolve(),
    )
    if args.mode in {"layer0", "full"}:
        app.run_layer_zero()
    if args.mode in {"layer1", "full"}:
        app.run_layer_one()


def _print_list_commands() -> None:
    print("module\tprofile\tdeprecated\treplacement")
    for module_path in sorted(MODULE_DEFINITIONS):
        definition = MODULE_DEFINITIONS[module_path]
        replacement = definition.replacement_module_path or "-"
        deprecated = "yes" if definition.deprecated else "no"
        print(f"{module_path}\t{definition.profile}\t{deprecated}\t{replacement}")


def main(argv: list[str] | None = None) -> None:
    parser = _build_main_parser()
    args, extra = parser.parse_known_args(argv)

    if args.command == "run":
        run_registered_module(args.module, extra)
        return

    if args.command == "domain":
        command = DOMAIN_COMMANDS[args.name]
        run_registered_module(command.module_path, extra)
        return

    if args.command == "wiki":
        wiki_args = [f"--mode={args.mode}", *extra]
        run_wiki_cli(wiki_args)
        return

    _print_list_commands()
