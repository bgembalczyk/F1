from scrapers.sponsorship_liveries.helpers.constants import POSSESSIVE_PAREN_RE


class DepthAwareColourSplitter:
    def __init__(self, text: str) -> None:
        self._text = text
        self._text_lower = text.lower()
        self._parts: list[str] = []
        self._current: list[str] = []
        self._depth = 0
        self._i = 0

    def split(self) -> list[str]:
        while self._i < len(self._text):
            char = self._text[self._i]
            if self._consume_parenthesis(char):
                continue
            if self._depth == 0 and self._consume_keyword_split():
                continue
            self._current.append(char)
            self._i += 1

        self._append_current_part()
        if len(self._parts) > 1 and POSSESSIVE_PAREN_RE.search(self._parts[-1]):
            return [self._text]
        return self._parts

    def _consume_parenthesis(self, char: str) -> bool:
        if char == "(":
            self._depth += 1
            self._current.append(char)
            self._i += 1
            return True
        if char == ")":
            self._depth = max(0, self._depth - 1)
            self._current.append(char)
            self._i += 1
            return True
        return False

    def _consume_keyword_split(self) -> bool:
        for keyword in (" and ", " or "):
            if self._text_lower[self._i : self._i + len(keyword)] != keyword:
                continue
            self._append_current_part()
            self._current = []
            self._i += len(keyword)
            return True
        return False

    def _append_current_part(self) -> None:
        part = "".join(self._current).strip()
        if part:
            self._parts.append(part)
