import re

HEADER_CLASS = "mw-body-header"
HEADER_TAG = "header"

HEADING_CLASS = "mw-heading2"


CURRENT_CONSTRUCTORS_ID = re.compile(r"^constructors for the (\d{4}) season$")


HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")


BASE_COMMON_ALIASES: dict[str, set[str]] = {
    "results": {"result", "results and standings", "grands prix"},
    "career results": {
        "racing record",
        "career record",
        "motorsport career results",
        "racing career",
    },
}
