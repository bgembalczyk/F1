import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import scripts.docs.generate_command_migration_map as generator
from scripts.docs.generate_command_migration_map import (
    _command_migration_map,
    build_generated_section,
    _replace_between_markers,
    main,
    BEGIN_MARKER,
    END_MARKER
)


def test_command_migration_map():
    with patch("scripts.docs.generate_command_migration_map.get_deprecated_module_migrations", return_value=[("old.module", "new.module")]):
        rows = _command_migration_map()
        assert len(rows) == 2
        assert rows[0] == ("python main.py", "from scrapers import run_wiki_flow; run_wiki_flow()")
        assert rows[1] == ("python -m old.module", "python -m new.module")


def test_build_generated_section():
    with patch("scripts.docs.generate_command_migration_map.get_deprecated_module_migrations", return_value=[("old", "new")]):
        out = build_generated_section()
        assert "### 7.2 Canonical command map (CLI/API)" in out
        assert "- `python main.py` -> `from scrapers import run_wiki_flow; run_wiki_flow()`" in out
        assert "- `python -m old` -> `python -m new`" in out
        assert out.endswith("\n")


def test_replace_between_markers_success():
    doc = f"A\n{BEGIN_MARKER}\nold\n{END_MARKER}\nB"
    generated = "new content"
    out = _replace_between_markers(doc, generated)
    expected = f"A\n{BEGIN_MARKER}\n\nnew content\n{END_MARKER}\nB"
    assert out == expected


def test_replace_between_markers_missing_begin():
    doc = f"A\nold\n{END_MARKER}\nB"
    with pytest.raises(ValueError, match="Nie znaleziono markerów"):
        _replace_between_markers(doc, "new")


def test_replace_between_markers_missing_end():
    doc = f"A\n{BEGIN_MARKER}\nold\nB"
    with pytest.raises(ValueError, match="Nie znaleziono markerów"):
        _replace_between_markers(doc, "new")


def test_main_check_up_to_date(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["script", "--check"])
    doc_content = f"A\n{BEGIN_MARKER}\n\nGENERATED\n{END_MARKER}\nB"

    mock_doc_path = MagicMock()
    mock_doc_path.read_text.return_value = doc_content
    monkeypatch.setattr(generator, "DOC_PATH", mock_doc_path)
    monkeypatch.setattr(generator, "build_generated_section", lambda: "GENERATED")

    assert main() == 0
    out, _ = capsys.readouterr()
    assert "zsynchronizowany" in out


def test_main_check_out_of_date(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["script", "--check"])
    doc_content = f"A\n{BEGIN_MARKER}\n\nOLD_GENERATED\n{END_MARKER}\nB"

    mock_doc_path = MagicMock()
    mock_doc_path.read_text.return_value = doc_content
    monkeypatch.setattr(generator, "DOC_PATH", mock_doc_path)
    monkeypatch.setattr(generator, "build_generated_section", lambda: "NEW_GENERATED")

    assert main() == 1
    out, _ = capsys.readouterr()
    assert "nieaktualny" in out


def test_main_write(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["script", "--write"])
    doc_content = f"A\n{BEGIN_MARKER}\n\nOLD_GENERATED\n{END_MARKER}\nB"

    mock_doc_path = MagicMock()
    mock_doc_path.read_text.return_value = doc_content
    monkeypatch.setattr(generator, "DOC_PATH", mock_doc_path)
    monkeypatch.setattr(generator, "build_generated_section", lambda: "NEW_GENERATED")

    assert main() == 0
    mock_doc_path.write_text.assert_called_once()
    out, _ = capsys.readouterr()
    assert "Zaktualizowano" in out


def test_main_print(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["script"])
    doc_content = f"A\n{BEGIN_MARKER}\n\nOLD_GENERATED\n{END_MARKER}\nB"

    mock_doc_path = MagicMock()
    mock_doc_path.read_text.return_value = doc_content
    monkeypatch.setattr(generator, "DOC_PATH", mock_doc_path)
    monkeypatch.setattr(generator, "build_generated_section", lambda: "NEW_GENERATED")

    assert main() == 0
    out, _ = capsys.readouterr()
    assert "NEW_GENERATED" in out
