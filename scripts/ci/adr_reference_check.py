#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from scripts.ci.reporting import CiReport
from scripts.ci.reporting import CiStatus
from scripts.ci.reporting import print_console_report

ADR_PATTERN = re.compile(r"\bADR-\d{4}\b", re.IGNORECASE)
ARCH_PATH_HINTS = (
    "layers/",
    "architecture",
    "importlinter.ini",
    "tests/architecture/",
)


def _changed_paths(csv_paths: str) -> list[str]:
    return [p.strip() for p in csv_paths.split(",") if p.strip()]


def _is_arch_change(paths: list[str]) -> bool:
    return any(path.startswith(ARCH_PATH_HINTS) or path == "importlinter.ini" for path in paths)


def _write_outputs(path: Path, status: CiStatus) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(f"adr_status={status.value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="ADR reference policy gate for architecture-impacting changes.")
    parser.add_argument("--changed-files", default="")
    parser.add_argument("--reference-text", default="")
    parser.add_argument("--github-output", required=True)
    args = parser.parse_args()

    changed = _changed_paths(args.changed_files)
    arch_change = _is_arch_change(changed)
    has_adr_reference = bool(ADR_PATTERN.search(args.reference_text))

    if not arch_change:
        report = CiReport(
            check_name="adr-reference",
            status=CiStatus.ok,
            summary="Brak zmian architektonicznych wymagających ADR.",
            recommendation="Brak akcji.",
        )
        print_console_report(report)
        _write_outputs(Path(args.github_output), CiStatus.ok)
        return 0

    if has_adr_reference:
        report = CiReport(
            check_name="adr-reference",
            status=CiStatus.ok,
            summary="Znaleziono referencję ADR dla zmian architektonicznych.",
            recommendation="Utrzymuj powiązanie zmian architektonicznych z decyzją ADR.",
        )
        print_console_report(report)
        _write_outputs(Path(args.github_output), CiStatus.ok)
        return 0

    report = CiReport(
        check_name="adr-reference",
        status=CiStatus.fail,
        summary="Wykryto zmianę architektoniczną bez referencji ADR-XXXX.",
        recommendation="Dodaj ADR-XXXX w tytule/opisie PR lub w commit message.",
        details=tuple(changed),
    )
    print_console_report(report)
    _write_outputs(Path(args.github_output), CiStatus.fail)
    return 1


if __name__ == "__main__":
    sys.exit(main())
