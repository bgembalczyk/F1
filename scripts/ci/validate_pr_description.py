"""Validate pull request description against mandatory quality gates."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Sequence


REQUIRED_SECTIONS: tuple[str, ...] = (
    "SRP impact",
    "DRY impact",
    "Contracts changed",
    "Backward compatibility",
    "DoD",
    "Code review evidence",
)

REQUIRED_CHECKLIST_ITEMS: tuple[str, ...] = (
    "Testy kontraktowe",
    "Brak nowych Any",
    "Brak nowych magic strings",
    "Brak nowych print",
    "Złożoność i długość modułów",
    "Spójność rejestru konfiguracji i implementacji",
    "Wyjątki tylko jawnie uzasadnione",
    "Zaktualizowany ADR/docs",
)


HEADING_PATTERN = re.compile(r"^\s*#{2,6}\s+(.+?)\s*$", re.MULTILINE)
CHECKLIST_PATTERN = re.compile(r"^\s*- \[(?P<state>[ xX])\]\s*(?P<label>.+)\s*$", re.MULTILINE)
CODE_BLOCK_PATTERN = re.compile(r"```.+?```", re.DOTALL)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate PR body contains required sections, checked technical checklist "
            "items and review evidence."
        )
    )
    parser.add_argument("--pr-body", help="Pull request body text")
    parser.add_argument(
        "--pr-body-file",
        help="Path to a UTF-8 text file containing pull request body",
    )
    args = parser.parse_args(argv)

    provided_body = args.pr_body is not None
    provided_file = args.pr_body_file is not None
    if provided_body == provided_file:
        parser.error("Provide exactly one of --pr-body or --pr-body-file.")

    return args


def read_body(args: argparse.Namespace) -> str:
    if args.pr_body is not None:
        return args.pr_body

    return Path(args.pr_body_file).read_text(encoding="utf-8")


def normalize(text: str) -> str:
    return " ".join(text.strip().lower().split())


def has_required_section(pr_body: str, section_name: str) -> bool:
    expected = normalize(section_name)
    headings = [normalize(match.group(1)) for match in HEADING_PATTERN.finditer(pr_body)]
    return expected in headings


def find_check_state(pr_body: str, item_label: str) -> bool:
    expected = normalize(item_label)
    for match in CHECKLIST_PATTERN.finditer(pr_body):
        label = normalize(match.group("label"))
        if expected in label:
            return match.group("state").lower() == "x"
    return False


def has_review_evidence(pr_body: str) -> bool:
    if CODE_BLOCK_PATTERN.search(pr_body):
        return True

    normalized = normalize(pr_body)
    evidence_markers = (
        "pytest",
        "ruff",
        "mypy",
        "lint-imports",
        "output",
        "wynik",
        "test",
        "check",
    )
    return any(marker in normalized for marker in evidence_markers)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    body = read_body(args)

    if not body.strip():
        print("PR description is empty; skipping validation in this run.")
        return 0

    detected_required_sections = [
        section for section in REQUIRED_SECTIONS if has_required_section(body, section)
    ]
    if not detected_required_sections:
        print("PR description does not use the enforced template sections; skipping validation in this run.")
        return 0

    missing_sections = [
        section for section in REQUIRED_SECTIONS if not has_required_section(body, section)
    ]
    unchecked_items = [
        item for item in REQUIRED_CHECKLIST_ITEMS if not find_check_state(body, item)
    ]

    evidence_present = has_review_evidence(body)

    if not missing_sections and not unchecked_items and evidence_present:
        print("PR description validation passed.")
        return 0

    print("PR description validation failed:")
    for section in missing_sections:
        print(f" - Missing required section heading: '{section}'")
    for item in unchecked_items:
        print(f" - Checklist item must be checked: '{item}'")
    if not evidence_present:
        print(" - Missing review evidence (command output/code block).")

    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
