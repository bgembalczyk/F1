import json
import re
import timeit
from pathlib import Path


def original(base_text, links):
    if not base_text:
        return None
    target = base_text.lower()
    best = None
    best_len = 0
    for link in links:
        link_text = link.get("text") or ""
        if not link_text:
            continue
        link_lower = link_text.lower()
        if target == link_lower:
            if len(link_text) > best_len:
                best = link
                best_len = len(link_text)
            continue
        remainder = target[len(link_lower) :]
        if target.startswith(link_lower) and re.sub(r"[\s\-—]", "", remainder):
            continue
        if target.startswith(link_lower):
            if len(link_text) > best_len:
                best = link
                best_len = len(link_text)
    return best


links = [
    {"text": "Sponsor A"},
    {"text": "Sponsor B"},
    {"text": "Sponsor C"},
    {"text": "Sponsor D —"},
    {"text": "Sponsor E -"},
    {"text": "Sponsor F "},
    {"text": "Sponsor G"},
    {"text": "Sponsor H"},
    {"text": "Sponsor I"},
    {"text": "Sponsor J"},
    {"text": "Sponsor D"},
]
base_text = "Sponsor D — "


def run_orig():
    original(base_text, links)


baseline_time = timeit.timeit(run_orig, number=100000)
print(f"BASELINE_TIME: {baseline_time}")

with Path("benchmark_results.json").open("w") as f:
    json.dump({"baseline": baseline_time}, f)
