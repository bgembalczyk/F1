# ruff: noqa: E501, PLR2004
"""Tests for RedFlaggedRacesBaseScraper (base.py methods)."""

from unittest.mock import patch

from bs4 import BeautifulSoup

from scrapers.races.columns.restart_status import RestartStatusColumn
from scrapers.races.red_flagged_races_scraper.base import RedFlaggedRacesBaseScraper


def _make_scraper(
    *,
    section_id: str | None = "Test_section",
    alternative_section_ids: list[str] | None = None,
    expected_headers: list[str] | None = None,
    table_css_class: str = "wikitable",
) -> RedFlaggedRacesBaseScraper:
    """Create a test scraper instance bypassing HTTP init."""

    class _Concrete(RedFlaggedRacesBaseScraper):
        pass

    with patch.object(
        RedFlaggedRacesBaseScraper,
        "__init__",
        lambda self, **kwargs: None,
    ):
        s = _Concrete.__new__(_Concrete)
        s.__init__()

    s.section_id = section_id
    s.section_domain = "grands_prix"
    s.alternative_section_ids = alternative_section_ids or []
    s.expected_headers = expected_headers or ["Year"]
    s.table_css_class = table_css_class
    return s


# ---------------------------------------------------------------------------
# build_common_red_flag_columns
# ---------------------------------------------------------------------------


def test_build_common_red_flag_columns_default_header() -> None:
    columns = RedFlaggedRacesBaseScraper.build_common_red_flag_columns()
    assert len(columns) == 9
    headers = [col.header for col in columns]
    assert "Year" in headers
    assert "Grand Prix" in headers
    assert "Lap" in headers
    assert "R" in headers


def test_build_common_red_flag_columns_custom_header() -> None:
    columns = RedFlaggedRacesBaseScraper.build_common_red_flag_columns("Event")
    headers = [col.header for col in columns]
    assert "Event" in headers
    assert "Grand Prix" not in headers


def test_build_common_red_flag_columns_restart_status_column() -> None:
    columns = RedFlaggedRacesBaseScraper.build_common_red_flag_columns()
    r_col = next(c for c in columns if c.header == "R")
    assert isinstance(r_col.column, RestartStatusColumn)


# ---------------------------------------------------------------------------
# _resolved_alternative_section_ids
# ---------------------------------------------------------------------------


def test_resolved_alternative_section_ids_no_section_id_returns_empty() -> None:
    s = _make_scraper(section_id=None)
    assert s._resolved_alternative_section_ids() == []


def test_resolved_alternative_section_ids_returns_list_of_strings() -> None:
    s = _make_scraper(
        section_id="World_Championship_races",
        alternative_section_ids=["Championship_races"],
    )
    alts = s._resolved_alternative_section_ids()
    assert isinstance(alts, list)
    # Each alternative should be a string (section ids)
    for alt in alts:
        assert isinstance(alt, str)


def test_resolved_alternative_section_ids_no_alternatives_returns_list() -> None:
    s = _make_scraper(section_id="Some_section", alternative_section_ids=[])
    alts = s._resolved_alternative_section_ids()
    assert isinstance(alts, list)


# ---------------------------------------------------------------------------
# _find_table_with_fallbacks
# ---------------------------------------------------------------------------


def test_find_table_with_fallbacks_no_table_returns_none_pair() -> None:
    s = _make_scraper()
    soup = BeautifulSoup("<html><body></body></html>", "html.parser")
    table, parser = s._find_table_with_fallbacks(soup)
    assert table is None
    assert parser is None


def test_find_table_with_fallbacks_finds_table_in_document() -> None:
    s = _make_scraper(section_id=None, expected_headers=["Year"])
    html = """
    <html><body>
    <table class="wikitable">
      <tr><th>Year</th><th>Grand Prix</th></tr>
      <tr><td>2024</td><td>Monaco</td></tr>
    </table>
    </body></html>
    """
    soup = BeautifulSoup(html, "html.parser")
    table, parser = s._find_table_with_fallbacks(soup)
    assert table is not None
    assert parser is not None


# ---------------------------------------------------------------------------
# _log_toc_diagnostics
# ---------------------------------------------------------------------------


def test_log_toc_diagnostics_no_section_id_does_not_raise() -> None:
    s = _make_scraper(section_id=None)
    soup = BeautifulSoup("<html></html>", "html.parser")
    s._log_toc_diagnostics(soup)  # should not raise


def test_log_toc_diagnostics_with_matching_toc_entry_logs_warning(caplog) -> None:
    import logging

    s = _make_scraper(section_id="Test_section")
    html = '<div id="toc-Test_section">TOC item</div>'
    soup = BeautifulSoup(html, "html.parser")

    with caplog.at_level(logging.WARNING):
        s._log_toc_diagnostics(soup)

    assert any("toc-Test_section" in msg for msg in caplog.messages)


def test_log_toc_diagnostics_no_toc_entry_no_warning(caplog) -> None:
    import logging

    s = _make_scraper(section_id="Test_section")
    soup = BeautifulSoup("<html></html>", "html.parser")

    with caplog.at_level(logging.WARNING):
        s._log_toc_diagnostics(soup)

    assert not any("toc-Test_section" in msg for msg in caplog.messages)


# ---------------------------------------------------------------------------
# _build_table_not_found_error
# ---------------------------------------------------------------------------


def test_build_table_not_found_error_returns_string() -> None:
    s = _make_scraper(section_id="Test_section")
    soup = BeautifulSoup("<html><body></body></html>", "html.parser")
    result = s._build_table_not_found_error(soup)
    assert isinstance(result, str)
    assert "Test_section" in result


def test_build_table_not_found_error_includes_table_count() -> None:
    s = _make_scraper(section_id="Test_section")
    html = '<table class="wikitable"><tr><th>Year</th></tr></table>'
    soup = BeautifulSoup(html, "html.parser")
    result = s._build_table_not_found_error(soup)
    assert "1" in result


def test_build_table_not_found_error_no_section_id() -> None:
    s = _make_scraper(section_id=None)
    soup = BeautifulSoup("<html></html>", "html.parser")
    result = s._build_table_not_found_error(soup)
    assert isinstance(result, str)
    assert "Nie znaleziono" in result
