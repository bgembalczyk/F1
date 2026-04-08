with open("tests/test_scraper_errors.py") as f:
    text = f.read()

import re

# remove the inline noqas
text = re.sub(r"  # noqa: E402", "", text)

# add file level noqa
if not text.startswith("# ruff: noqa"):
    text = "# ruff: noqa: E402\n" + text

with open("tests/test_scraper_errors.py", "w") as f:
    f.write(text)
