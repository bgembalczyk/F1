import time
import timeit
from bs4 import BeautifulSoup

def baseline(soup):
    records = [
        {"text": li.get_text(" ", strip=True)}
        for li in soup.select("ul li")
        if li.get_text(" ", strip=True)
    ]
    return records

def optimized(soup):
    records = [
        {"text": text}
        for li in soup.select("ul li")
        if (text := li.get_text(" ", strip=True))
    ]
    return records

def run_benchmark():
    html = "<html><body>" + "<ul><li>  hello  </li><li></li><li>world</li></ul>" * 1000 + "</body></html>"
    soup = BeautifulSoup(html, 'html.parser')

    # Warmup
    baseline(soup)
    optimized(soup)

    baseline_time = timeit.timeit(lambda: baseline(soup), number=100)
    optimized_time = timeit.timeit(lambda: optimized(soup), number=100)

    print(f"Baseline: {baseline_time:.4f} s")
    print(f"Optimized: {optimized_time:.4f} s")
    print(f"Improvement: {(baseline_time - optimized_time) / baseline_time * 100:.2f}%")

if __name__ == "__main__":
    run_benchmark()
