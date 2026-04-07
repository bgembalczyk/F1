import timeit

from bs4 import BeautifulSoup

html_content = (
    """
<div>
  <p>Some paragraph text """
    + ("<b>bold</b> <i>italic</i> " * 50)
    + """</p>
  <ul>
"""
    + ("    <li>Item with nested tags " + ("<span>text</span>" * 50) + "</li>\n") * 50
    + """
  </ul>
</div>
"""
    * 10
)


def test_original():
    soup = BeautifulSoup(html_content, "html.parser")
    return [
        {"text": li.get_text(" ", strip=True)}
        for li in soup.select("ul li")
        if li.get_text(" ", strip=True)
    ]


def test_walrus():
    soup = BeautifulSoup(html_content, "html.parser")
    return [
        {"text": text}
        for li in soup.select("ul li")
        if (text := li.get_text(" ", strip=True))
    ]


print("Original:", timeit.timeit(test_original, number=100))
print("Walrus:", timeit.timeit(test_walrus, number=100))
