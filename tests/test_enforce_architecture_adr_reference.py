from __future__ import annotations

from types import SimpleNamespace

from scripts.ci import enforce_architecture_adr_reference as adr_gate


def test_classify_diff_line_comment_with_code_is_not_cosmetic() -> None:
    assert adr_gate.classify_diff_line("value = 1  # komentarz") == "code"


def test_python_ast_semantically_changed_ignores_docstring_only_changes() -> None:
    base_source = '''
def fn():
    """Old docs."""
    return 1
'''
    head_source = '''
def fn():
    """New docs."""
    return 1
'''
    assert not adr_gate.python_ast_semantically_changed(base_source, head_source)


def test_has_non_cosmetic_changes_in_file_treats_import_reorder_as_cosmetic(
    monkeypatch,
) -> None:
    diff_output = """diff --git a/sample.py b/sample.py
--- a/sample.py
+++ b/sample.py
@@ -1,2 +1,2 @@
-import os
-import sys
+import sys
+import os
"""

    def _fake_run(cmd, check, capture_output, text):  # type: ignore[no-untyped-def]
        if cmd[:2] == ["git", "diff"]:
            return SimpleNamespace(returncode=0, stdout=diff_output)
        if cmd[:2] == ["git", "show"]:
            if cmd[2].startswith("base:"):
                return SimpleNamespace(returncode=0, stdout="import os\nimport sys\n")
            if cmd[2].startswith("head:"):
                return SimpleNamespace(returncode=0, stdout="import sys\nimport os\n")
        return SimpleNamespace(returncode=1, stdout="")

    monkeypatch.setattr(adr_gate.subprocess, "run", _fake_run)

    assert not adr_gate.has_non_cosmetic_changes_in_file("base", "head", "sample.py")
