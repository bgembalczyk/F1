from __future__ import annotations

import re
import sys
import types


def ensure_bs4_stub() -> None:
    if "bs4" in sys.modules:
        return
    sys.modules["bs4"] = _build_bs4_stub_module()


def _build_bs4_stub_module() -> types.ModuleType:
    bs4_stub = types.ModuleType("bs4")
    bs4_stub.Tag = _StubTag
    bs4_stub.BeautifulSoup = _StubBeautifulSoup
    return bs4_stub


class _StubTag:
    def __init__(self, attrs=None, text: str = ""):
        self.attrs = attrs or {}
        self.text = text

    def get(self, key, default=None):
        return self.attrs.get(key, default)

    def get_text(self, *_, **__):
        return self.text

    def find_all(self, *_, **__):
        return []

    def find_all_next(self, *_, **__):
        return []

    @property
    def contents(self):
        return [self.text]


class _StubBeautifulSoup:
    def __init__(self, html: str, *_):
        self.html = html

    def find(self, name: str | None = None, *_, **__):
        if name == "a":
            return self._parse_a(self.html)
        return _StubTag()

    def find_all(self, *_, **__):
        return []

    def _parse_a(self, html: str) -> _StubTag:
        attrs = self._parse_anchor_attrs(html)
        return _StubTag(attrs, self._parse_anchor_text(html))

    @staticmethod
    def _parse_anchor_attrs(html: str) -> dict[str, object]:
        attrs: dict[str, object] = {}
        href_match = re.search(r'href="([^"]*)"', html)
        class_match = re.search(r'class="([^"]*)"', html)
        if href_match:
            attrs["href"] = href_match.group(1)
        if class_match:
            attrs["class"] = class_match.group(1).split()
        return attrs

    @staticmethod
    def _parse_anchor_text(html: str) -> str:
        text_match = re.search(r">([^<]*)<", html)
        return text_match.group(1) if text_match else ""


def ensure_certifi_stub() -> None:
    if "certifi" not in sys.modules:
        certifi_stub = types.ModuleType("certifi")
        certifi_stub.where = lambda: ""
        sys.modules["certifi"] = certifi_stub
