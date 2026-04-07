import timeit

from scrapers.drivers.infobox.parsers.nationality import NationalityParser

text = "British (1963, 1965-1968) French (1970) Italian (1980, 1982-1985)" * 100


def bench():
    NationalityParser._extract_years_from_text(text)  # noqa: SLF001


if __name__ == "__main__":
    n = 1000
    t = timeit.timeit(bench, number=n)
    print(f"Baseline: {t / n * 1000:.4f} ms per call")
