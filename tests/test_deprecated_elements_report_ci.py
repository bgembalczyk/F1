from __future__ import annotations

from datetime import date

from scripts.ci.deprecated_elements_report import _build_rows


def test_deprecated_report_rows_have_required_fields() -> None:
    rows, expired = _build_rows(date(2026, 4, 2))

    assert rows
    assert not expired
    for row in rows:
        assert row["module"].startswith("scrapers.")
        assert row["deprecated_since"]
        assert row["replacement"]
        assert row["remove_after"]
        assert row["status"] in {"active", "expired"}
