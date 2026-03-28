import timeit

text = " ".join(["2000-2005", "2008", "2010-2012", "2014-2015", "2018", "2020-2022", "2023"] * 100)

setup_uncompiled = "import re\ntext = '" + text + "'"

stmt_uncompiled = """
for match in re.finditer(r"\\b(\\d{4})\\s*[--]\\s*(\\d{2,4})\\b", text):
    pass
for match in re.finditer(r"\\b(\\d{4})\\b", text):
    pass
"""

setup_compiled = "import re\ntext = '" + text + "'\nYEAR_RANGE_RE = re.compile(r\"\\b(\\d{4})\\s*[--]\\s*(\\d{2,4})\\b\")\nYEAR_RE = re.compile(r\"\\b(\\d{4})\\b\")"

stmt_compiled = """
for match in YEAR_RANGE_RE.finditer(text):
    pass
for match in YEAR_RE.finditer(text):
    pass
"""

uncompiled_time = timeit.timeit(stmt_uncompiled, setup=setup_uncompiled, number=1000)
compiled_time = timeit.timeit(stmt_compiled, setup=setup_compiled, number=1000)

print(f"Uncompiled: {uncompiled_time:.5f}s")
print(f"Compiled:   {compiled_time:.5f}s")
print(f"Improvement: {(uncompiled_time - compiled_time) / uncompiled_time * 100:.2f}%")
