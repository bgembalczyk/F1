import importlib.util
import sys
import types
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

if importlib.util.find_spec("requests") is None:
    requests_stub = types.ModuleType("requests")

    class _RequestException(Exception):
        pass

    class _Session:
        def get(self, *_args, **_kwargs):
            msg = "requests stub"
            raise _RequestException(msg)

    requests_stub.RequestException = _RequestException
    requests_stub.Session = _Session
    sys.modules["requests"] = requests_stub

if importlib.util.find_spec("certifi") is None:
    certifi_stub = types.ModuleType("certifi")

    def _where():
        return ""

    certifi_stub.where = _where
    sys.modules["certifi"] = certifi_stub

if importlib.util.find_spec("pandas") is None:
    pandas_stub = types.ModuleType("pandas")

    class _StubDataFrame:
        def __init__(self, *_args, **_kwargs):
            pass

    pandas_stub.DataFrame = _StubDataFrame
    sys.modules["pandas"] = pandas_stub

if importlib.util.find_spec("bs4") is None:
    bs4_stub = types.ModuleType("bs4")

    class _Tag:
        pass

    class _BeautifulSoup:
        def __init__(self, *_args, **_kwargs):
            pass

    bs4_stub.Tag = _Tag
    bs4_stub.BeautifulSoup = _BeautifulSoup
    sys.modules["bs4"] = bs4_stub


@pytest.fixture
def minimal_fetch_html() -> str:
    fixture_path = Path(__file__).parent / "fixtures" / "minimal_fetch.html"
    return fixture_path.read_text(encoding="utf-8")
