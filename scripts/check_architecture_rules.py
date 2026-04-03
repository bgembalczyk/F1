#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

SCRAPER_DOMAIN_PARTS = 3


def _load_architecture_rules() -> Any:
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

    from tests.architecture import rules

    return rules


def _iter_layer_files(
    domain_dir: Path,
    domain: str,
    rules: Any,
) -> list[tuple[Path, str]]:
    collected: list[tuple[Path, str]] = []
    for py_file in domain_dir.rglob("*.py"):
        layer = rules.infer_layer(py_file, domain=domain)
        if layer in rules.LAYERS:
            collected.append((py_file, layer))
    return collected


def _detect_relevant_domains(
    changed_files: list[Path],
    *,
    domains: tuple[str, ...],
) -> set[str]:
    selected: set[str] = set()
    for file_path in changed_files:
        parts = file_path.parts
        if (
            len(parts) >= SCRAPER_DOMAIN_PARTS
            and parts[0] == "scrapers"
            and parts[1] in domains
        ):
            selected.add(parts[1])
    return selected


def _check_required_layout(
    root: Path,
    domains: tuple[str, ...],
    rules: Any,
) -> list[str]:
    violations: list[str] = []
    for domain in domains:
        domain_dir = root / domain
        if not domain_dir.exists():
            violations.append(f"Missing domain directory: {domain_dir}")
            continue

        entrypoint = domain_dir / "entrypoint.py"
        if not entrypoint.exists():
            violations.append(f"Missing facade entrypoint in domain: {domain}")

        available_layers = {
            layer for _, layer in _iter_layer_files(domain_dir, domain, rules)
        }
        missing_layers = set(rules.REQUIRED_LAYERS_BY_DOMAIN[domain]) - available_layers
        if missing_layers:
            violations.append(
                f"Missing layer modules for {domain}: {sorted(missing_layers)}",
            )
    return violations


def _check_layer_boundaries(
    root: Path,
    domains: tuple[str, ...],
    rules: Any,
) -> list[str]:
    violations: list[str] = []
    for domain in domains:
        domain_dir = root / domain
        if not domain_dir.exists():
            continue

        for py_file, layer in _iter_layer_files(domain_dir, domain, rules):
            targets = rules.resolve_import_targets(py_file)
            forbidden = rules.FORBIDDEN_IMPORTS_BY_LAYER[layer]
            for forbidden_target in forbidden:
                dotted = f"scrapers.{domain}.{forbidden_target}"
                if any(
                    target == dotted or target.startswith(f"{dotted}.")
                    for target in targets
                ):
                    violations.append(
                        "Layer boundary violation: "
                        f"{py_file} imports {dotted}; targets={targets}",
                    )
    return violations


def _check_cross_domain_imports(
    root: Path,
    domains: tuple[str, ...],
    rules: Any,
) -> list[str]:
    violations: list[str] = []
    for domain in domains:
        domain_dir = root / domain
        if not domain_dir.exists():
            continue

        for py_file in domain_dir.rglob("*.py"):
            cross_domain = rules.collect_cross_domain_import_violations(py_file, domain)
            if cross_domain:
                uniq = sorted(set(cross_domain))
                violations.append(f"Cross-domain import in {py_file}: {uniq}")
    return violations


def _check_sections_single_scraper_boundary(
    root: Path,
    domains: tuple[str, ...],
    rules: Any,
) -> list[str]:
    violations: list[str] = []
    for domain in domains:
        sections_dir = root / domain / "sections"
        if not sections_dir.exists():
            continue

        for py_file in sections_dir.glob("*.py"):
            imports = rules.collect_single_scraper_import_violations(py_file, domain)
            if imports:
                violations.append(
                    "Forbidden import direction sections/ -> single_scraper.py "
                    f"in {py_file}: {imports}",
                )
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fast architecture boundary checks for local lint/CI.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional changed files (pre-commit mode).",
    )
    args = parser.parse_args()

    rules = _load_architecture_rules()

    root = Path("scrapers")
    changed_files = [Path(path) for path in args.paths if path.endswith(".py")]
    relevant_domains = _detect_relevant_domains(
        changed_files,
        domains=rules.DOMAINS,
    )

    if relevant_domains:
        full_domains = tuple(
            domain for domain in rules.ENTRYPOINT_DOMAINS if domain in relevant_domains
        )
        all_domains = tuple(
            domain for domain in rules.DOMAINS if domain in relevant_domains
        )
    else:
        full_domains = rules.ENTRYPOINT_DOMAINS
        all_domains = rules.DOMAINS

    errors = [
        *_check_required_layout(root, full_domains, rules),
        *_check_layer_boundaries(root, full_domains, rules),
        *_check_sections_single_scraper_boundary(root, full_domains, rules),
        *_check_cross_domain_imports(root, all_domains, rules),
    ]

    if errors:
        print("Architecture rules check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Architecture rules check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
