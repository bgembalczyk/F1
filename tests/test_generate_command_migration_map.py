"""Unit tests for scripts/docs/generate_command_migration_map.py."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from scripts.docs import generate_command_migration_map as gcm

if TYPE_CHECKING:
    from pathlib import Path

# ---------------------------------------------------------------------------
# build_generated_section
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_build_generated_section_returns_string() -> None:
    result = gcm.build_generated_section()
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.unit()
def test_build_generated_section_contains_migration_header() -> None:
    result = gcm.build_generated_section()
    assert "command map" in result.lower() or "7.2" in result


@pytest.mark.unit()
def test_build_generated_section_ends_with_newline() -> None:
    result = gcm.build_generated_section()
    assert result.endswith("\n")


# ---------------------------------------------------------------------------
# _replace_between_markers
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_replace_between_markers_replaces_section() -> None:
    doc = f"Before\n{gcm.BEGIN_MARKER}\nOld content\n{gcm.END_MARKER}\nAfter"
    result = gcm._replace_between_markers(doc, "New content\n")
    assert "Old content" not in result
    assert "New content" in result
    assert "Before" in result
    assert "After" in result


@pytest.mark.unit()
def test_replace_between_markers_raises_on_missing_markers() -> None:
    doc = "No markers here"
    with pytest.raises(ValueError, match="markery"):
        gcm._replace_between_markers(doc, "replacement")


@pytest.mark.unit()
def test_replace_between_markers_preserves_markers() -> None:
    doc = f"A\n{gcm.BEGIN_MARKER}\nX\n{gcm.END_MARKER}\nB"
    result = gcm._replace_between_markers(doc, "Y\n")
    assert gcm.BEGIN_MARKER in result
    assert gcm.END_MARKER in result


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


@pytest.mark.unit()
def test_main_prints_generated_section_by_default(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with patch("sys.argv", ["generate_command_migration_map"]):
        result = gcm.main()
    assert result == 0
    captured = capsys.readouterr()
    assert len(captured.out) > 0


@pytest.mark.unit()
def test_main_check_mode_reports_not_in_sync_when_stale(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    # Create a stale doc that doesn't match the generated content
    stale_content = (
        f"Prefix\n{gcm.BEGIN_MARKER}\nStale content here\n{gcm.END_MARKER}\nSuffix\n"
    )
    fake_doc = tmp_path / "MODULE_BOUNDARIES.md"
    fake_doc.write_text(stale_content, encoding="utf-8")

    with (
        patch.object(gcm, "DOC_PATH", fake_doc),
        patch("sys.argv", ["generate_command_migration_map", "--check"]),
    ):
        result = gcm.main()

    # Since content is stale, should return 1
    assert result == 1
    captured = capsys.readouterr()
    assert "nieaktualny" in captured.out


@pytest.mark.unit()
def test_main_check_mode_reports_ok_when_in_sync(
    capsys: pytest.CaptureFixture[str],
    tmp_path: Path,
) -> None:
    # Create a doc that is in sync with the generated content
    fake_doc = tmp_path / "MODULE_BOUNDARIES.md"
    # First generate what the current content should be
    with patch.object(gcm, "DOC_PATH", fake_doc):
        # Bootstrap with stale content first
        stale = f"A\n{gcm.BEGIN_MARKER}\nX\n{gcm.END_MARKER}\nB\n"
        fake_doc.write_text(stale, encoding="utf-8")
        # Write it to sync
        with patch("sys.argv", ["generate_command_migration_map", "--write"]):
            gcm.main()
        # Now check it's in sync
        with patch("sys.argv", ["generate_command_migration_map", "--check"]):
            result = gcm.main()

    assert result == 0
    captured = capsys.readouterr()
    assert "zsynchronizowany" in captured.out


@pytest.mark.unit()
def test_main_write_mode_writes_to_doc(tmp_path: Path) -> None:
    # Create a temporary doc with the required markers
    doc_content = f"Prefix\n{gcm.BEGIN_MARKER}\nOld\n{gcm.END_MARKER}\nSuffix\n"
    fake_doc = tmp_path / "MODULE_BOUNDARIES.md"
    fake_doc.write_text(doc_content, encoding="utf-8")

    with (
        patch.object(gcm, "DOC_PATH", fake_doc),
        patch("sys.argv", ["generate_command_migration_map", "--write"]),
    ):
        result = gcm.main()
    assert result == 0
    updated = fake_doc.read_text(encoding="utf-8")
    assert "Old" not in updated
    assert gcm.BEGIN_MARKER in updated
