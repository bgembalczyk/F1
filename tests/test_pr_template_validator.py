from __future__ import annotations

from scripts.ci.validate_pr_template import extract_architecture_fields
from scripts.ci.validate_pr_template import has_checked_checkbox
from scripts.ci.validate_pr_template import normalize_field_value
from scripts.ci.validate_pr_template import touches_scrapers_base


def test_has_checked_checkbox_detects_checked_items() -> None:
    body = """
- [x] **Brak nowych `Any`**: ok
- [ ] **Duplikacja**: todo
"""

    assert has_checked_checkbox(body, "Brak nowych `Any`")
    assert not has_checked_checkbox(body, "Duplikacja")


def test_extract_architecture_fields_reads_required_lines() -> None:
    body = """
- Zmiany w `scrapers/base/`: nie dotyczy
- Dotknięte domeny: drivers
- Kompatybilność wsteczna: tak
- Migracja wymagana: nie
"""

    fields = extract_architecture_fields(body)

    assert fields["Zmiany w `scrapers/base/`"] == "nie dotyczy"
    assert fields["Dotknięte domeny"] == "drivers"


def test_touches_scrapers_base_detects_base_changes() -> None:
    files = ["scrapers/base/results.py", "models/records/driver.py"]
    assert touches_scrapers_base(files)
    assert not touches_scrapers_base(["models/records/driver.py"])


def test_normalize_field_value_removes_html_comments() -> None:
    value = "<!-- hint --> Nie dotyczy "
    assert normalize_field_value(value) == "nie dotyczy"
