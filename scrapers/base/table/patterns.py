"""Shared regex patterns for table column parsing."""

import re

# Pattern for time in 12-hour format with am/pm
TIME_12H_PATTERN = re.compile(r"(\d{1,2}):(\d{2})\s*(am|pm)", re.IGNORECASE)

# Pattern for range separators
SEPARATOR_PATTERN = re.compile(r"\s*[-—]\s*")
