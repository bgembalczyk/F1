from __future__ import annotations

from pathlib import Path

from scripts.ci.generate_architecture_spec_doc import render_markdown


def test_architecture_spec_doc_is_synced_with_code_spec() -> None:
    doc_path = Path("docs/architecture/ARCHITECTURE_SPEC.md")
    assert doc_path.exists(), "Missing generated architecture spec doc."

    expected = render_markdown()
    actual = doc_path.read_text(encoding="utf-8")

    assert actual == expected, (
        "Architecture spec doc is out of sync with source spec. "
        "Run: python scripts/ci/generate_architecture_spec_doc.py"
    )
