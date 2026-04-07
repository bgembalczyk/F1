import time
import timeit
from bs4 import BeautifulSoup

from scrapers.drivers.infobox.parsers.championships import ChampionshipsParser
from scrapers.drivers.infobox.parsers.link_extractor import InfoboxLinkExtractor

def run_benchmark():
    link_extractor = InfoboxLinkExtractor(include_urls=True, wikipedia_base="https://en.wikipedia.org")
    parser = ChampionshipsParser(link_extractor)

    html1 = "<td>2 (2015, 2016)</td>"
    cell1 = BeautifulSoup(html1, 'html.parser').td

    html2 = "<td>6 <small>(1969, 1970, 1971, 1975, 1976, 1977)</small></td>"
    cell2 = BeautifulSoup(html2, 'html.parser').td

    def bench_champs():
        parser._parse_championships_payload(cell1, "2 (2015, 2016)")

    def bench_wins():
        parser._parse_class_wins_payload(cell2, "6 (1969, 1970, 1971, 1975, 1976, 1977)")

    champs_time = timeit.timeit(bench_champs, number=10000)
    wins_time = timeit.timeit(bench_wins, number=10000)

    print(f"Championships parser: {champs_time:.4f} seconds")
    print(f"Class wins parser: {wins_time:.4f} seconds")

if __name__ == "__main__":
    run_benchmark()
