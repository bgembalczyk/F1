# ruff: noqa: PERF401
from __future__ import annotations

from pathlib import Path

from scrapers.base.sections.constants import DOMAIN_SECTION_RESOLVER_CONFIG
from tests.architecture.registry import ARCHITECTURE_REGISTRY
from tests.support.imports_analyzer import parse_imports

ENTRYPOINT_DOMAINS = ARCHITECTURE_REGISTRY.entrypoint_domains


def _is_forbidden_single_scraper_import(
    *,
    domain: str,
    imported_module: str | None,
    import_level: int,
) -> bool:
    if imported_module is None:
        return False

    absolute_target = f"scrapers.{domain}.single_scraper"
    relative_target = "single_scraper"

    return imported_module == absolute_target or (
        import_level > 0 and imported_module == relative_target
    )


def _collect_import_violations(py_file: Path, domain: str) -> list[str]:
    violations: list[str] = []
    for parsed_import in parse_imports(py_file):
        if _is_forbidden_single_scraper_import(
            domain=domain,
            imported_module=parsed_import.module,
            import_level=parsed_import.level,
        ):
            violations.append(
                f"{'.' * parsed_import.level}{parsed_import.module}",
            )
    return violations


def test_sections_modules_do_not_import_single_scraper() -> None:
    root = Path("scrapers")
    for domain in ENTRYPOINT_DOMAINS:
        sections_dir = root / domain / "sections"
        for py_file in sections_dir.glob("*.py"):
            violations = _collect_import_violations(py_file, domain)
            assert not violations, (
                "Forbidden import direction sections/ -> single_scraper.py "
                f"in {py_file}: {violations}"
            )


def test_single_scraper_can_depend_on_sections_without_reverse_dependency() -> None:
    root = Path("scrapers")
    for domain in ENTRYPOINT_DOMAINS:
        single_scraper_file = root / domain / "single_scraper.py"
        assert (
            single_scraper_file.exists()
        ), f"Missing single scraper file in domain: {single_scraper_file}"

        sections_dir = root / domain / "sections"
        violating_modules = [
            py_file
            for py_file in sections_dir.glob("*.py")
            if _collect_import_violations(py_file, domain)
        ]
        assert not violating_modules, (
            "single_scraper.py may import sections/, but sections/ must not "
            f"import single_scraper.py for domain={domain}: {violating_modules}"
        )


def test_critical_sections_have_alias_fallbacks() -> None:
    for domain in ENTRYPOINT_DOMAINS:
        critical = DOMAIN_SECTION_RESOLVER_CONFIG.get(domain, ())
        assert critical, f"Missing critical sections map for domain={domain}"
        for section in critical:
            assert section.section_id.strip(), f"Empty section id in domain={domain}"
            assert section.alternative_section_ids, (
                f"Critical section without aliases in domain={domain}, "
                f"section={section.section_id}"
            )
