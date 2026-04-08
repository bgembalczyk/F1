# ruff: noqa: E501, PLR2004
from bs4 import BeautifulSoup

from scrapers.base.helpers.sections import get_category_texts
from scrapers.base.helpers.sections import has_category_keyword
from scrapers.base.helpers.sections import has_navbox_template_link


def soup_with_catlinks(links: list[str]) -> BeautifulSoup:
    li_items = "".join(f'<li><a href="/wiki/{t}">{t}</a></li>' for t in links)
    html = f'<div id="mw-normal-catlinks"><ul>{li_items}</ul></div>'
    return BeautifulSoup(html, "html.parser")


def soup_no_catlinks() -> BeautifulSoup:
    return BeautifulSoup("<div>no cats here</div>", "html.parser")


def test_get_category_texts_returns_empty_when_no_catlinks() -> None:
    # Line 10: return []
    result = get_category_texts(soup_no_catlinks())
    assert result == []


def test_get_category_texts_returns_lowercased_texts() -> None:
    soup = soup_with_catlinks(["Formula_One", "Racing"])
    result = get_category_texts(soup)
    assert "formula_one" in result
    assert "racing" in result


def test_has_category_keyword_true_when_keyword_present() -> None:
    soup = soup_with_catlinks(["Formula_One_seasons"])
    assert has_category_keyword(soup, ["formula_one"]) is True


def test_has_category_keyword_false_when_no_match() -> None:
    soup = soup_with_catlinks(["SomeOtherCategory"])
    assert has_category_keyword(soup, ["formula_one"]) is False


def soup_with_navbox(href_fragment: str) -> BeautifulSoup:
    html = f"""
    <table class="navbox-inner">
        <tr><td><a href="/wiki/{href_fragment}">Link</a></td></tr>
    </table>
    """
    return BeautifulSoup(html, "html.parser")


def test_has_navbox_template_link_true_when_fragment_found() -> None:
    # Lines 25-29
    soup = soup_with_navbox("Template:F1_seasons")
    assert has_navbox_template_link(soup, "Template:F1") is True


def test_has_navbox_template_link_false_when_fragment_not_found() -> None:
    soup = soup_with_navbox("Template:F1_seasons")
    assert has_navbox_template_link(soup, "Template:WRC") is False


def test_has_navbox_template_link_no_navboxes_returns_false() -> None:
    soup = BeautifulSoup("<div>no navbox</div>", "html.parser")
    assert has_navbox_template_link(soup, "Template:F1") is False
