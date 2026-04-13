import pytest
from bs4 import BeautifulSoup

from scrapers.columns.context import ColumnContext


BASE_URL = "https://en.wikipedia.org"


@pytest.fixture()
def html_valid_record_results() -> str:
    return (
        '<td><a href="/wiki/Scuderia_Ferrari">Scuderia Ferrari</a>'
        "<sup>12</sup><sup>†</sup><sup>*</sup></td>"
    )


@pytest.fixture()
def html_incomplete_record_results() -> str:
    return "<td></td>"


@pytest.fixture()
def html_alias_or_text_record_results() -> str:
    return "<td>half points awarded</td>"


@pytest.fixture()
def html_links_and_no_links_record_results() -> tuple[str, str]:
    return (
        '<td><a href="/wiki/Team_Lotus">Team Lotus</a></td>',
        "<td>No sponsors listed</td>",
    )


def ctx_from_html_results(html: str) -> ColumnContext:
    cell = BeautifulSoup(html, "html.parser").find("td")
    links = [
        {"text": a.get_text(strip=True), "url": f"{BASE_URL}{a.get('href')}"}
        for a in cell.find_all("a")
    ]
    text = cell.get_text(" ", strip=True)
    return ColumnContext(
        header="Results",
        key="results",
        raw_text=text,
        clean_text=text,
        links=links,
        cell=cell,
        base_url=BASE_URL,
    )


@pytest.fixture()
def html_valid_record_driver() -> str:
    return '<td><a href="/wiki/Lewis_Hamilton">Lewis Hamilton</a></td>'


@pytest.fixture()
def html_incomplete_record_driver() -> str:
    return "<td>Unknown driver</td>"


@pytest.fixture()
def html_alias_or_text_record_driver() -> str:
    return '<td><a href="/wiki/Lewis_Hamilton">Sir Lewis Hamilton</a></td>'


@pytest.fixture()
def html_links_and_no_links_record_driver() -> tuple[str, str]:
    return (
        '<td><a href="/wiki/Max_Verstappen">Max Verstappen</a></td>',
        "<td>Reserve entry</td>",
    )


def ctx_from_html_driver(html: str) -> ColumnContext:
    cell = BeautifulSoup(html, "html.parser").find("td")
    links = [
        {"text": a.get_text(strip=True), "url": f"{BASE_URL}{a.get('href')}"}
        for a in cell.find_all("a")
    ]
    text = cell.get_text(" ", strip=True)
    return ColumnContext(
        header="Driver",
        key="driver",
        raw_text=text,
        clean_text=text,
        links=links,
        cell=cell,
        base_url=BASE_URL,
    )


@pytest.fixture()
def html_valid_record_constructor() -> str:
    return (
        '<td><a href="/wiki/Ferrari">Ferrari</a><br>'
        '<a href="/wiki/Mercedes-Benz_in_Formula_One">Mercedes</a></td>'
    )


@pytest.fixture()
def html_incomplete_record_constructor() -> str:
    return "<td>Ferrari -</td>"


@pytest.fixture()
def html_alias_or_text_record_constructor() -> str:
    return "<td>Scuderia Alpha - Team Beta</td>"


@pytest.fixture()
def html_links_and_no_links_record_constructor() -> tuple[str, str]:
    with_links = (
        '<td><a href="/wiki/McLaren">McLaren</a> '
        '<a href="/wiki/Ford_Motor_Company">Ford</a></td>'
    )
    without_links = "<td>Lotus - Climax</td>"
    return with_links, without_links


def ctx_from_html_constructor(html: str) -> ColumnContext:
    cell = BeautifulSoup(html, "html.parser").find("td")
    links = [
        {"text": a.get_text(strip=True), "url": f"{BASE_URL}{a.get('href')}"}
        for a in cell.find_all("a")
    ]
    text = cell.get_text(" ", strip=True)
    return ColumnContext(
        header="Constructor",
        key="constructor",
        raw_text=text,
        clean_text=text,
        links=links,
        cell=cell,
        base_url=BASE_URL,
    )


