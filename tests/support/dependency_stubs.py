from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
import types

import pytest


def ensure_optional_deps(*, require_bs4: bool, bs4_skip_reason: str) -> None:
    _ensure_requests_stub()
    _ensure_certifi_stub()
    _ensure_pandas_stub()
    _ensure_bs4_stub(require_bs4=require_bs4, bs4_skip_reason=bs4_skip_reason)


def _module_exists(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except ValueError:
        sys.modules.pop(module_name, None)
        return False


def _ensure_requests_stub() -> None:
    if _module_exists("requests"):
        return
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


def _ensure_certifi_stub() -> None:
    if _module_exists("certifi"):
        return
    certifi_stub = types.ModuleType("certifi")
    certifi_stub.where = lambda: ""
    sys.modules["certifi"] = certifi_stub


def _ensure_pandas_stub() -> None:
    if _module_exists("pandas"):
        return
    pandas_stub = types.ModuleType("pandas")
    pandas_stub.__spec__ = importlib.machinery.ModuleSpec("pandas", loader=None)

    class _StubDataFrame:
        def __init__(self, data=None, *_args, **_kwargs):
            self._rows = data if isinstance(data, list) else []
            first_row = self._rows[0] if self._rows else {}
            self.columns = list(first_row.keys()) if isinstance(first_row, dict) else []

        @property
        def iloc(self):
            class _StubILoc:
                def __init__(self, rows):
                    self._rows = rows

                def __getitem__(self, index):
                    class _StubRow:
                        def __init__(self, row):
                            self._row = row if isinstance(row, dict) else {}

                        def to_dict(self):
                            return dict(self._row)

                    return _StubRow(self._rows[index])

            return _StubILoc(self._rows)

    pandas_stub.DataFrame = _StubDataFrame
    sys.modules["pandas"] = pandas_stub


def _ensure_bs4_stub(*, require_bs4: bool, bs4_skip_reason: str) -> None:
    if _module_exists("bs4"):
        return
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
