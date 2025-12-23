from typing import Sequence


def is_repeated_header_row(
    cells: Sequence[str],
    headers: Sequence[str],
) -> bool:
    return len(cells) == len(headers) and list(cells) == list(headers)
