"""Validate pull request description against mandatory quality gates."""

from __future__ import annotations

import argparse
import re
import sys
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
    "Zaktualizowany ADR/docs",
)


HEADING_PATTERN = re.compile(r"^\s{0,3}#{2,6}\s+(.+?)\s*$", re.MULTILINE)
CHECKLIST_PATTERN = re.compile(r"- \[(?P<state>[ xX])\]\s*(?P<label>.+)")
CODE_BLOCK_PATTERN = re.compile(r"```.+?```", re.DOTALL)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate PR body contains required sections, checked technical checklist "
            "items and review evidence."
        )
    )
    parser.add_argument("--pr-body", required=True, help="Pull request body text")
    return parser.parse_args(argv)


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
    body = args.pr_body or ""

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
