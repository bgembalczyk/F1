from bs4 import BeautifulSoup


def soup_func(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


