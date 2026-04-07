import re
import timeit
import json

REMAINDER_CLEANUP_RE = re.compile(r"[\s\-—]")

def optimized(base_text, links):
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
        if target.startswith(link_lower):
            remainder = target[len(link_lower) :]
            if REMAINDER_CLEANUP_RE.sub("", remainder):
                continue
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

def run_opt():
    optimized(base_text, links)

opt_time = timeit.timeit(run_opt, number=100000)
print(f"OPTIMIZED_TIME: {opt_time}")

with open("benchmark_results.json", "r") as f:
    results = json.load(f)

baseline = results["baseline"]
improvement = baseline - opt_time
pct_improvement = (improvement / baseline) * 100

print(f"Baseline: {baseline:.4f}s")
print(f"Optimized: {opt_time:.4f}s")
print(f"Improvement: {improvement:.4f}s ({pct_improvement:.2f}%) faster")

results["optimized"] = opt_time
results["pct_improvement"] = pct_improvement

with open("benchmark_results.json", "w") as f:
    json.dump(results, f)
