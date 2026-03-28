from __future__ import annotations

import importlib.util
import sys
import types

import pytest


def ensure_optional_deps(*, require_bs4: bool, bs4_skip_reason: str) -> None:
    if importlib.util.find_spec("requests") is None:
        requests_stub = types.ModuleType("requests")

        class _RequestError(Exception):
            pass

        class _Session:
            def get(self, *_args, **_kwargs):
                msg = "requests stub"
                raise _RequestError(msg)

        requests_stub.RequestException = _RequestError
        requests_stub.Session = _Session
        sys.modules["requests"] = requests_stub

    if importlib.util.find_spec("certifi") is None:
        certifi_stub = types.ModuleType("certifi")
        certifi_stub.where = lambda: ""
        sys.modules["certifi"] = certifi_stub

    if importlib.util.find_spec("pandas") is None:
        pandas_stub = types.ModuleType("pandas")

        class _StubDataFrame:
            def __init__(self, *_args, **_kwargs):
                pass

        pandas_stub.DataFrame = _StubDataFrame
        sys.modules["pandas"] = pandas_stub

    if importlib.util.find_spec("bs4") is None:
        if require_bs4:
            pytest.skip(bs4_skip_reason, allow_module_level=True)
        bs4_stub = types.ModuleType("bs4")

        class _Tag:
            pass

        class _BeautifulSoup:
            def __init__(self, *_args, **_kwargs):
                pass

        bs4_stub.Tag = _Tag
        bs4_stub.BeautifulSoup = _BeautifulSoup
        sys.modules["bs4"] = bs4_stub
