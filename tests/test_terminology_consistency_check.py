from __future__ import annotations

from pathlib import Path

from scripts.ci.check_terminology_consistency import TerminologyRule
from scripts.ci.check_terminology_consistency import scan_files
from scripts.ci.check_terminology_consistency import scan_text_forbidden_terms


def test_scan_text_forbidden_terms_detects_forbidden_synonym() -> None:
    rules = (TerminologyRule(canonical="grand_prix", forbidden=("grandprix",)),)

    issues = scan_text_forbidden_terms("class GrandprixParser: pass", rules)

    assert issues == [(1, "grandprix", "grand_prix")]


def test_scan_files_reports_file_and_line(tmp_path: Path) -> None:
    target = tmp_path / "bad.md"
    target.write_text("Termin grand_prixes jest zabroniony", encoding="utf-8")

    rules = (TerminologyRule(canonical="grands_prix", forbidden=("grand_prixes",)),)
    errors = scan_files([target], rules)

    assert errors == [
        f"{target}:1: znaleziono zabroniony termin 'grand_prixes' (użyj canonical: 'grands_prix')"
    ]
