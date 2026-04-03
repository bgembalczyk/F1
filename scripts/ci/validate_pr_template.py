from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import PurePosixPath

from scripts.ci.quality_gate_constants import NOT_APPLICABLE_VALUES

REQUIRED_HEADINGS: tuple[str, ...] = (
    "## Opis zmiany",
    "## Checklist (quality gate)",
    "## Architecture impact",
    "## Refactor included",
)

REQUIRED_CHECKBOXES: tuple[str, ...] = (
    "Brak nowych `Any`",
    "Granice modułów",
    "Duplikacja",
    "Złożoność i długość modułów",
    "Brak nowych print/magic strings/defaultów",
    "Spójność rejestru konfiguracji i implementacji",
    "Wyjątki tylko jawnie uzasadnione",
    "Architecture impact",
    "Spójność terminologiczna",
)

ARCHITECTURE_IMPACT_FIELDS: tuple[str, ...] = (
    "Zmiany w `scrapers/base/`",
    "Dotknięte domeny",
    "Kompatybilność wsteczna",
    "Migracja wymagana",
)
GIT_BIN = shutil.which("git") or "git"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Waliduje obecność wymaganych pól i checklisty z PR template, "
            "w tym sekcji Architecture impact."
        ),
    )
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--pr-body", default="")
    return parser.parse_args()


def list_changed_files(base_sha: str, head_sha: str) -> list[str]:
    # nosec B603 -- zaufane wywołanie lokalnego `git`
    proc = subprocess.run(
        [GIT_BIN, "diff", "--name-only", "--diff-filter=ACMR", base_sha, head_sha],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def touches_scrapers_base(files: list[str]) -> bool:
    return any(
        PurePosixPath(path).as_posix().startswith("scrapers/base/") for path in files
    )


def normalize_field_value(value: str) -> str:
    return re.sub(r"<!--.*?-->", "", value, flags=re.DOTALL).strip().lower()


def extract_architecture_fields(pr_body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for field in ARCHITECTURE_IMPACT_FIELDS:
        match = re.search(
            rf"^-\s*{re.escape(field)}\s*:\s*(.*)$",
            pr_body,
            flags=re.MULTILINE,
        )
        fields[field] = match.group(1).strip() if match else ""
    return fields


def has_checked_checkbox(pr_body: str, label: str) -> bool:
    pattern = re.compile(rf"^-\s*\[[xX]\]\s*\*\*{re.escape(label)}", re.MULTILINE)
    return bool(pattern.search(pr_body))


def main() -> int:
    args = parse_args()
    pr_body = args.pr_body.strip()

    if not pr_body:
        print("::error::Pusty opis PR. Uzupełnij PR template.")
        return 1

    field_values = extract_architecture_fields(pr_body)
    errors = _collect_template_errors(pr_body, field_values)

    changed_files = list_changed_files(args.base_sha, args.head_sha)
    requires_detailed_impact = touches_scrapers_base(changed_files)

    if requires_detailed_impact:
        errors.extend(_validate_detailed_architecture_impact(field_values))

    if errors:
        for err in errors:
            print(f"::error::{err}")
        return 1

    print("Walidacja PR template zakończona sukcesem.")
    return 0


def _collect_template_errors(
    pr_body: str,
    field_values: dict[str, str],
) -> list[str]:
    errors: list[str] = []
    errors.extend(_missing_headings(pr_body))
    errors.extend(_unchecked_checkboxes(pr_body))
    errors.extend(_missing_architecture_fields(field_values))
    return errors


def _missing_headings(pr_body: str) -> list[str]:
    return [
        f"Brak sekcji: {heading}"
        for heading in REQUIRED_HEADINGS
        if heading not in pr_body
    ]


def _unchecked_checkboxes(pr_body: str) -> list[str]:
    return [
        f"Checklista niepotwierdzona: {checkbox}"
        for checkbox in REQUIRED_CHECKBOXES
        if not has_checked_checkbox(pr_body, checkbox)
    ]


def _missing_architecture_fields(field_values: dict[str, str]) -> list[str]:
    return [
        f"Brak wartości pola: {field}"
        for field, value in field_values.items()
        if not value
    ]


def _validate_detailed_architecture_impact(field_values: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for field, raw_value in field_values.items():
        normalized = normalize_field_value(raw_value)
        if normalized and normalized not in NOT_APPLICABLE_VALUES:
            continue
        errors.append(
            "Zmiany w scrapers/base wymagają uzupełnionej sekcji "
            "Architecture impact; "
            f"pole '{field}' nie może mieć wartości 'nie dotyczy'.",
        )
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
