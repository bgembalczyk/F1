from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from scrapers.wiki import flow_entrypoint


class _FacadeSpy:
    def __init__(self) -> None:
        self.calls = 0

    def run_full(self) -> None:
        self.calls += 1


def test_run_wiki_flow_routes_to_default_facade(monkeypatch, tmp_path: Path) -> None:
    facade = _FacadeSpy()

    monkeypatch.setattr(
        flow_entrypoint,
        "DEFAULT_PATH_RESOLVER",
        SimpleNamespace(exports_root=tmp_path / "wiki", debug_root=tmp_path / "debug"),
    )
    monkeypatch.setattr(
        flow_entrypoint,
        "create_default_wiki_pipeline_facade",
        lambda **_kwargs: facade,
    )

    flow_entrypoint.run_wiki_flow()

    assert facade.calls == 1
