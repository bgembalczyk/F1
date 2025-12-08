import sys
import types

try:
    import bs4  # type: ignore
except ModuleNotFoundError:
    from tests import bs4_stub

    sys.modules["bs4"] = bs4_stub

if "certifi" not in sys.modules:
    certifi_stub = types.SimpleNamespace(where=lambda: None)
    sys.modules["certifi"] = certifi_stub
