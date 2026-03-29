from __future__ import annotations

from pathlib import Path

from tests.architecture.rules import DOMAINS
from tests.architecture.rules import ENTRYPOINT_DOMAINS
from tests.architecture.rules import ENTRYPOINT_MODULES

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


def test_configured_entrypoint_modules_exist() -> None:
    missing_entrypoint_modules = [
        module_path
        for module_path in ENTRYPOINT_MODULES
        if not Path(module_path).exists()
    ]

    assert not missing_entrypoint_modules, (
        "Configured entrypoint module paths do not exist. "
        "Update tests/architecture/rules.py ENTRYPOINT_MODULES. "
        f"missing={missing_entrypoint_modules}"
    )
