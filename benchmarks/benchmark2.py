import timeit

from bs4 import BeautifulSoup

html_content = (
    """
<div id="mid-season_changes">
    <p>   Some mid-season changes text.   </p>
    <p></p>
    <p>   More text.   </p>
    <p>    </p>
    <ul>
        <li>  Change 1  </li>
        <li>  </li>
        <li>  Change 2  </li>
        <li>  Change 3  </li>
        <li>    </li>
    </ul>
    <li> Or maybe just li elements </li>
    <li> </li>
</div>
"""
    * 100
)  # Repeat to make it larger

soup = BeautifulSoup(html_content, "html.parser")


def current_parse():
    return [
        {"text": p.get_text(" ", strip=True)}
        for p in soup.find_all("p")
        if p.get_text(" ", strip=True)
    ]


def new_parse():
    return [
        {"text": text}
        for p in soup.find_all("p")
        if (text := p.get_text(" ", strip=True))
    ]


def current_extract_list_items():
    return [
        {"text": li.get_text(" ", strip=True)}
        for li in soup.select("ul li")
        if li.get_text(" ", strip=True)
    ]


def new_extract_list_items():
    return [
        {"text": text}
        for li in soup.select("ul li")
        if (text := li.get_text(" ", strip=True))
    ]


if __name__ == "__main__":
    n = 1000

    t_curr_parse = timeit.timeit(current_parse, number=n)
    t_new_parse = timeit.timeit(new_parse, number=n)

    t_curr_ext = timeit.timeit(current_extract_list_items, number=n)
    t_new_ext = timeit.timeit(new_extract_list_items, number=n)

    parse_improvement = (t_curr_parse - t_new_parse) / t_curr_parse * 100
    extract_improvement = (t_curr_ext - t_new_ext) / t_curr_ext * 100

    print(f"Current Parse (p tags): {t_curr_parse:.4f}s")
    print(f"New Parse (p tags):     {t_new_parse:.4f}s")
    print(f"Improvement Parse:      {parse_improvement:.2f}%")

    print(f"Current Extract (li tags): {t_curr_ext:.4f}s")
    print(f"New Extract (li tags):     {t_new_ext:.4f}s")
    print(f"Improvement Extract:       {extract_improvement:.2f}%")
