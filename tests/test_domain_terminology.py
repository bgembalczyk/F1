import pytest
from pathlib import Path
from scripts.lib.domain_terminology import parse_forbidden_term_map

def test_parse_forbidden_term_map(tmp_path):
    p = tmp_path / "glossary.md"
    content = """
Some text
```
# Comments should be ignored
bad -> good
wrong -> right
missing_arrow
```
More text
"""
    p.write_text(content)
    mapping = parse_forbidden_term_map(p)
    assert mapping == {
        "bad": "good",
        "wrong": "right"
    }

def test_parse_forbidden_term_map_empty(tmp_path):
    p = tmp_path / "glossary.md"
    p.write_text("No code block here")
    mapping = parse_forbidden_term_map(p)
    assert mapping == {}
