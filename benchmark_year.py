import timeit
import re

# Setup different test cases
test_cases = [
    "(until 2019)",
    "(2020-)",
    "(2015-2018)",
    "(2020-present)",
    "(2015)",
    "2001, 2003-2005"
]

MIN_RANGE_YEARS = 2

def original_parse_licence_years(year_text: str) -> dict[str, int | None]:
    years: dict[str, int | None] = {"start": None, "end": None}
    year_text = year_text.strip("()")
    if "until" in year_text.lower():
        year_match = re.search(r"\b(\d{4})\b", year_text)
        if year_match:
            years["end"] = int(year_match.group(1))
    elif re.search(r"\b(\d{4})\s*[-\u2013]\s*(?:present)?$", year_text.strip()):
        year_match = re.search(r"\b(\d{4})\b", year_text)
        if year_match:
            years["start"] = int(year_match.group(1))
    else:
        all_years = re.findall(r"\b(\d{4})\b", year_text)
        if len(all_years) >= MIN_RANGE_YEARS:
            years["start"] = int(all_years[0])
            years["end"] = int(all_years[-1])
        elif len(all_years) == 1:
            years["start"] = int(all_years[0])
            years["end"] = int(all_years[0])
    return years

YEAR_RE = re.compile(r"\b(\d{4})\b")
OPEN_ENDED_RE = re.compile(r"\b(\d{4})\s*[-\u2013]\s*(?:present)?$")

def optimized_parse_licence_years(year_text: str) -> dict[str, int | None]:
    years: dict[str, int | None] = {"start": None, "end": None}
    year_text = year_text.strip("()")

    # Extract all years upfront using the compiled regex
    all_years = YEAR_RE.findall(year_text)

    if "until" in year_text.lower():
        if all_years:
            years["end"] = int(all_years[0])
    elif OPEN_ENDED_RE.search(year_text.strip()):
        if all_years:
            years["start"] = int(all_years[0])
    else:
        if len(all_years) >= MIN_RANGE_YEARS:
            years["start"] = int(all_years[0])
            years["end"] = int(all_years[-1])
        elif len(all_years) == 1:
            years["start"] = int(all_years[0])
            years["end"] = int(all_years[0])
    return years

def run_benchmarks():
    # Verify outputs match
    for tc in test_cases:
        assert original_parse_licence_years(tc) == optimized_parse_licence_years(tc), f"Mismatch on {tc}"

    def test_original():
        for tc in test_cases:
            original_parse_licence_years(tc)

    def test_optimized():
        for tc in test_cases:
            optimized_parse_licence_years(tc)

    n_iterations = 100000

    orig_time = timeit.timeit(test_original, number=n_iterations)
    opt_time = timeit.timeit(test_optimized, number=n_iterations)

    print(f"Original time: {orig_time:.4f}s")
    print(f"Optimized time: {opt_time:.4f}s")
    print(f"Improvement: {((orig_time - opt_time) / orig_time) * 100:.2f}%")

if __name__ == '__main__':
    run_benchmarks()
