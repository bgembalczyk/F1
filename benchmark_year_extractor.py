import timeit
from scrapers.base.helpers.year_extraction import YearExtractor
import sys

# Mock modules for testing environment
from unittest.mock import MagicMock
sys.modules['bs4'] = MagicMock()
sys.modules['pandas'] = MagicMock()

def test_extract_years():
    text = "F1 races occurred in 2002, 2005, 2007. There were also races in the 2010-2012 period, and a short range like 2018-19."
    YearExtractor.extract_years_from_text(text)

if __name__ == "__main__":
    n = 100000
    baseline_time = timeit.timeit(test_extract_years, number=n)
    print(f"Time for {n} executions: {baseline_time:.4f} seconds")
