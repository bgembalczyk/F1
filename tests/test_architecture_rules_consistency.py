from __future__ import annotations

from pathlib import Path

from tests.architecture.rules import DOMAINS
from tests.architecture.rules import ENTRYPOINT_DOMAINS

IGNORED_PACKAGES = {"base", "wiki", "__pycache__"}


def test_domains_registry_has_directory_and_entrypoint() -> None:
    root = Path("scrapers")
    missing_dirs = [domain for domain in DOMAINS if not (root / domain).is_dir()]
    missing_entrypoints = [
        domain for domain in DOMAINS if not (root / domain / "entrypoint.py").is_file()
    ]

    assert not missing_dirs, f"Missing domain directories: {sorted(missing_dirs)}"
    assert not missing_entrypoints, (
        "Every domain from scrapers.domains.DOMAINS must expose an entrypoint. "
        f"missing={sorted(missing_entrypoints)}"
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
        "Update scrapers/domains.py DOMAINS. "
        f"discovered={sorted(discovered_entrypoint_domains)} configured={sorted(ENTRYPOINT_DOMAINS)}"
    )
