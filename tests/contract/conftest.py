# ruff: noqa: PT001
import sys
from pathlib import Path

import pytest

from tests.support.dependency_stubs import ensure_optional_deps

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

ensure_optional_deps(require_bs4=False, bs4_skip_reason="")


@pytest.fixture()
def minimal_fetch_html() -> str:
    fixture_path = Path(__file__).parent / "fixtures" / "minimal_fetch.html"
    return fixture_path.read_text(encoding="utf-8")
