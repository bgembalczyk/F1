from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING

from scrapers.wiki import flow_entrypoint

if TYPE_CHECKING:
    from pathlib import Path


class _ApplicationSpy:
    def __init__(self) -> None:
        self.calls = 0

    def run_full(self) -> None:
        self.calls += 1


def test_run_wiki_flow_routes_to_default_application(monkeypatch, tmp_path: Path) -> None:
    application = _ApplicationSpy()

    monkeypatch.setattr(
        flow_entrypoint,
        "DEFAULT_PATH_RESOLVER",
        SimpleNamespace(exports_root=tmp_path / "wiki", debug_root=tmp_path / "debug"),
    )
    monkeypatch.setattr(
        flow_entrypoint,
        "create_default_wiki_pipeline_application",
        lambda **_kwargs: application,
    )

    flow_entrypoint.run_wiki_flow()

    assert application.calls == 1
