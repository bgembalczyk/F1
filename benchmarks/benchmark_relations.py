import re
import timeit


def original_parse(links, text):
    entries = []
    for link in links:
        relation = None
        pattern = rf"{re.escape(link.get('text') or '')}\s*\(([^)]+)\)"
        match = re.search(pattern, text)
        if match:
            relation = match.group(1).strip()
        entries.append({"person": link, "relation": relation})
    return entries


RELATION_PATTERN = re.compile(r"\s*\(([^)]+)\)")


def optimized_parse_static(links, text):
    entries = []
    matches = list(RELATION_PATTERN.finditer(text))

    for link in links:
        relation = None
        t = link.get("text") or ""

        if t:
            for match in matches:
                start_idx = match.start()
                if start_idx >= len(t):
                    if text[start_idx - len(t) : start_idx] == t:
                        relation = match.group(1).strip()
                        break
        elif matches:
            relation = matches[0].group(1).strip()

        entries.append({"person": link, "relation": relation})
    return entries


def benchmark():
    # In a real scraper, there are hundreds/thousands of different strings.
    # The cache would be thrashing in `original_parse`.
    # Let's simulate a cache thrashing scenario.

    import random
    import string

    def r_str(n=5):
        return "".join(random.choices(string.ascii_letters, k=n))

    t_orig = 0
    t_opt = 0

    for _ in range(500):
        # We generate 10 unique names and relations each iteration
        # Total links per iteration: 10
        # Re-evaluating 500 times = 5000 unique regex compilations
        # This will quickly overflow the 512 maxcache!
        re.purge()
        names = [r_str() for _ in range(10)]
        rels = [r_str() for _ in range(10)]
        text = " ".join(f"{n} ({r})" for n, r in zip(names, rels, strict=False))
        links = [{"text": n, "url": ""} for n in names]
        links.append({"text": "", "url": ""})

        start = timeit.default_timer()
        original_parse(links, text)
        t_orig += timeit.default_timer() - start

        start = timeit.default_timer()
        optimized_parse_static(links, text)
        t_opt += timeit.default_timer() - start

    print(f"Original: {t_orig:.4f} s")
    print(f"Optimized Static: {t_opt:.4f} s")
    print(f"Improvement: {t_orig / t_opt:.2f}x")


benchmark()
