from __future__ import annotations

from importlib import import_module
from pathlib import Path

from scrapers.wiki.flow_entrypoint import run_wiki_flow


def test_wiki_flow_entrypoint_is_callable() -> None:
    assert callable(run_wiki_flow)


def test_main_entrypoint_uses_package_flow() -> None:
    source = Path("main.py").read_text(encoding="utf-8")
    assert "from scrapers import run_wiki_flow" in source
    assert "run_wiki_flow()" in source
