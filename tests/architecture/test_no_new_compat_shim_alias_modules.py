from __future__ import annotations

from pathlib import Path

# ADR-0008: infrastructure-only exceptions.
ADR_INFRA_EXCEPTIONS = {
    "infrastructure/http/type_alias.py",
    "infrastructure/http/errors/shim/__init__.py",
    "infrastructure/http/errors/shim/base.py",
    "infrastructure/http/errors/shim/http.py",
    "infrastructure/http/errors/shim/response_adapter.py",
    "infrastructure/http/errors/shim/timeout.py",
}

# Baseline modules already present before this guard was introduced.
LEGACY_BASELINE_ALLOWLIST = {
    "models/domain_utils/field_normalization/aliases.py",
    "models/mappers/field_aliases.py",
    "models/records/factories/compat.py",
    "scrapers/module_naming_aliases.py",
    "scrapers/section/aliases.py",
    "scrapers/seed_l0_compat_wiki.py",
    "scrapers/source_adapter_fetcher_shim.py",
}


def _looks_like_compat_module(path: Path) -> bool:
    lowered_parts = [part.lower() for part in path.parts]
    stem = path.stem.lower()
    token_in_stem = any(token in stem for token in ("compat", "shim", "alias"))
    token_in_parts = any(part in {"compat", "shim", "aliases"} for part in lowered_parts)
    return token_in_stem or token_in_parts


def test_no_new_compat_shim_alias_modules_outside_adr_exceptions() -> None:
    roots = ("scrapers", "models", "layers", "infrastructure")

    discovered = {
        path.as_posix()
        for root in roots
        for path in Path(root).rglob("*.py")
        if _looks_like_compat_module(path)
    }

    unknown = sorted(discovered - ADR_INFRA_EXCEPTIONS - LEGACY_BASELINE_ALLOWLIST)
    assert not unknown, (
        "New compat/shim/alias modules are forbidden. "
        "Only ADR-0008 infrastructure exceptions are allowed. "
        f"Unexpected modules: {', '.join(unknown)}"
    )
