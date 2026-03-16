from __future__ import annotations

from pathlib import Path

DOMAINS = ("drivers", "constructors", "circuits", "seasons", "grands_prix")
LAYERS = ("list", "sections", "infobox", "postprocess")

FORBIDDEN_IMPORTS_BY_LAYER = {
    "list": ("sections", "infobox", "postprocess"),
    "sections": ("list_scraper", "single_scraper"),
    "infobox": ("sections", "list", "postprocess"),
    "postprocess": ("sections", "list", "infobox"),
}


def test_domains_have_required_layout_and_facade_entrypoint() -> None:
    root = Path("scrapers")
    for domain in DOMAINS:
        domain_dir = root / domain
        assert domain_dir.exists(), f"Missing domain directory: {domain_dir}"
        assert (domain_dir / "entrypoint.py").exists(), (
            f"Missing facade entrypoint in domain: {domain}"
        )
        for layer in LAYERS:
            layer_dir = domain_dir / layer
            assert layer_dir.exists(), f"Missing layer directory: {layer_dir}"
            assert (layer_dir / "__init__.py").exists(), (
                f"Missing layer package init: {layer_dir / '__init__.py'}"
            )


def test_layer_import_boundaries_are_not_violated() -> None:
    root = Path("scrapers")
    for domain in DOMAINS:
        domain_dir = root / domain
        for layer, forbidden in FORBIDDEN_IMPORTS_BY_LAYER.items():
            layer_dir = domain_dir / layer
            for py_file in layer_dir.glob("*.py"):
                source = py_file.read_text(encoding="utf-8")
                for forbidden_target in forbidden:
                    dotted = f"scrapers.{domain}.{forbidden_target}"
                    slashed = f"scrapers/{domain}/{forbidden_target}"
                    assert dotted not in source, (
                        f"Layer boundary violation: {py_file} imports {dotted}"
                    )
                    assert slashed not in source, (
                        f"Layer boundary violation: {py_file} references {slashed}"
                    )
