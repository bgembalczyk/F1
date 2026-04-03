from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from scrapers import cli


class _FacadeSpy:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def run_scenario(self, scenario: str) -> None:
        self.calls.append(scenario)


def test_parse_wiki_cli_args_supports_merge_scenario() -> None:
    args = cli._parse_wiki_cli_args(["--scenario", "merge"])  # noqa: SLF001

    assert args.scenario == "merge"


def test_run_wiki_cli_routes_to_facade(monkeypatch) -> None:
    facade = _FacadeSpy()

    monkeypatch.setattr(cli, "configure_logging", lambda **_kwargs: None)
    monkeypatch.setattr(
        cli,
        "DEFAULT_PATH_RESOLVER",
        SimpleNamespace(exports_root=Path("/tmp/wiki"), debug_root=Path("/tmp/debug")),
    )
    monkeypatch.setattr(
        cli.importlib,
        "import_module",
        lambda _name: SimpleNamespace(
            create_default_wiki_pipeline_facade=lambda **_kwargs: facade,
        ),
    )

    cli.run_wiki_cli(["--mode", "merge"])

    assert facade.calls == ["merge"]
