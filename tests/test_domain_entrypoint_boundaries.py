from __future__ import annotations

from pathlib import Path

from tests.architecture.rules import ENTRYPOINT_DOMAINS
from tests.architecture.rules import FORBIDDEN_IMPORTS_BY_LAYER
from tests.architecture.rules import LAYERS
from tests.architecture.rules import REQUIRED_LAYERS_BY_DOMAIN
from tests.architecture.rules import infer_layer
from tests.architecture.rules import resolve_import_targets


def _iter_layer_files(domain_dir: Path, domain: str) -> list[tuple[Path, str]]:
    collected: list[tuple[Path, str]] = []
    for py_file in domain_dir.rglob("*.py"):
        layer = infer_layer(py_file, domain=domain)
        if layer in LAYERS:
            collected.append((py_file, layer))
    return collected


def test_domains_have_required_layout_and_facade_entrypoint() -> None:
    root = Path("scrapers")
    for domain in ENTRYPOINT_DOMAINS:
        domain_dir = root / domain
        assert domain_dir.exists(), f"Missing domain directory: {domain_dir}"
        assert (
            domain_dir / "entrypoint.py"
        ).exists(), f"Missing facade entrypoint in domain: {domain}"

        available_layers = {layer for _, layer in _iter_layer_files(domain_dir, domain)}
        required_layers = set(REQUIRED_LAYERS_BY_DOMAIN[domain])
        missing_layers = required_layers - available_layers
        assert not missing_layers, f"Missing layer modules for {domain}: {sorted(missing_layers)}"


def test_layer_import_boundaries_are_not_violated() -> None:
    root = Path("scrapers")
    for domain in ENTRYPOINT_DOMAINS:
        domain_dir = root / domain
        for py_file, layer in _iter_layer_files(domain_dir, domain):
            targets = resolve_import_targets(py_file)
            forbidden = FORBIDDEN_IMPORTS_BY_LAYER[layer]
            for forbidden_target in forbidden:
                dotted = f"scrapers.{domain}.{forbidden_target}"
                assert all(
                    not (target == dotted or target.startswith(f"{dotted}."))
                    for target in targets
                ), f"Layer boundary violation: {py_file} imports {dotted}; targets={targets}"
