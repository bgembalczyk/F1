import timeit

setup = """
from models.domain_utils.years import _parse_explicit_range_match

texts = [
    "1990-1995",
    "2000-present",
    "from 2010 to 2015",
    "between 1980 and 1985",
    "just 2020",
    "2001-05",
    "1999 to present"
]
"""

stmt = """
for text in texts:
    _parse_explicit_range_match(text)
"""

print("Baseline:", timeit.timeit(stmt, setup=setup, number=10000))
