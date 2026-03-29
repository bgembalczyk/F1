from __future__ import annotations

from pathlib import Path

from tests.architecture.rules import DOMAINS
from tests.architecture.rules import ENTRYPOINT_DOMAINS

IGNORED_PACKAGES = {"base", "wiki", "__pycache__"}


def test_domains_registry_matches_scrapers_packages() -> None:
    root = Path("scrapers")
    discovered_domains = {
        path.name
        for path in root.iterdir()
        if path.is_dir() and path.name not in IGNORED_PACKAGES
    }

    assert discovered_domains == set(DOMAINS), (
        "Architecture domains list is out of sync with scrapers packages. "
        f"Update tests/architecture/rules.py DOMAINS. "
        f"discovered={sorted(discovered_domains)} configured={sorted(DOMAINS)}"
    )


def test_entrypoint_domains_registry_matches_domains_with_entrypoints() -> None:
    root = Path("scrapers")
    discovered_entrypoint_domains = {
        path.name
        for path in root.iterdir()
        if path.is_dir() and (path / "entrypoint.py").exists()
    }

    assert discovered_entrypoint_domains == set(ENTRYPOINT_DOMAINS), (
        "Entrypoint domains list is out of sync with current code. "
        f"Update tests/architecture/rules.py ENTRYPOINT_DOMAINS. "
        f"discovered={sorted(discovered_entrypoint_domains)} configured={sorted(ENTRYPOINT_DOMAINS)}"
    )
