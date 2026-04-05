import pytest

from scrapers.base.errors import ScraperParseError
from scrapers.base.parsers.safe_parser_mixin import SafeParserMixin


class _StubHandler:
    def __init__(self, *, should_handle: bool) -> None:
        self.should_handle = should_handle
        self.last_wrapped_url = None
        self.handled_errors = []

    def wrap_parse(self, exc: Exception, *, url: str | None = None):
        self.last_wrapped_url = url
        return ScraperParseError("wrapped parser error", url=url, cause=exc)

    def handle(self, error: ScraperParseError) -> bool:
        self.handled_errors.append(error)
        return self.should_handle


class _ParserHarness(SafeParserMixin):
    def __init__(self, *, should_handle: bool, url_provider=None) -> None:
        self.error_handler = _StubHandler(should_handle=should_handle)
        self._url_provider = url_provider


def test_safe_parse_returns_empty_result_without_degradation() -> None:
    parser = _ParserHarness(
        should_handle=True,
        url_provider=lambda: "https://example.com",
    )

    result = parser._safe_parse(list)

    assert result == []
    assert parser.error_handler.handled_errors == []


def test_safe_parse_wraps_exception_and_degrades_to_none_on_soft_handle() -> None:
    parser = _ParserHarness(
        should_handle=True,
        url_provider=lambda: "https://example.com",
    )

    result = parser._safe_parse(lambda: (_ for _ in ()).throw(ValueError("bad parse")))

    assert result is None
    assert parser.error_handler.last_wrapped_url == "https://example.com"
    assert len(parser.error_handler.handled_errors) == 1


def test_safe_parse_rethrows_wrapped_error_when_soft_handling_disabled() -> None:
    parser = _ParserHarness(should_handle=False, url_provider=None)

    with pytest.raises(ScraperParseError) as exc_info:
        parser._safe_parse(lambda: (_ for _ in ()).throw(ValueError("bad normalizer")))
    assert exc_info.value.url is None
    assert isinstance(exc_info.value.cause, ValueError)


def test_safe_parse_rethrows_original_scraper_error_when_already_wrapped() -> None:
    parser = _ParserHarness(
        should_handle=False,
        url_provider=lambda: "https://example.com",
    )
    original = ScraperParseError("parser dependency failed")

    with pytest.raises(ScraperParseError) as exc_info:
        parser._safe_parse(lambda: (_ for _ in ()).throw(original))
    assert exc_info.value is original
