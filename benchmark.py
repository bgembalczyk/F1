import timeit
from bs4 import BeautifulSoup
from scrapers.seasons.sections.mid_season_changes import SeasonMidSeasonChangesSectionParser

html_content = """
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
""" * 100 # Repeat to make it larger

soup = BeautifulSoup(html_content, 'html.parser')

def test_parse():
    parser = SeasonMidSeasonChangesSectionParser()
    parser.parse(soup)

def test_extract_list_items():
    parser = SeasonMidSeasonChangesSectionParser()
    parser._extract_list_items(soup)

if __name__ == "__main__":
    n = 1000
    time_parse = timeit.timeit(test_parse, number=n)
    time_extract = timeit.timeit(test_extract_list_items, number=n)
    print(f"parse: {time_parse:.4f}s for {n} iterations")
    print(f"extract_list_items: {time_extract:.4f}s for {n} iterations")
