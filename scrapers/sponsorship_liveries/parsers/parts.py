class SponsorPartsParser:
    def __init__(self, text: str) -> None:
        self._text = text
        self._parts: list[tuple[str, str]] = []
        self._current: list[str] = []
        self._depth = 0
        self._after_close_paren = False

    def parse(self) -> list[tuple[str, str]]:
        for char in self._text:
            self._update_depth_state(char)
            if self._try_split_on_separator(char):
                continue
            self._try_implicit_split_after_paren(char)
            self._current.append(char)
        self._append_current("")
        return self._parts

    def _update_depth_state(self, char: str) -> None:
        if char == "(":
            self._depth += 1
            self._after_close_paren = False
        elif char == ")":
            self._depth = max(self._depth - 1, 0)
            if self._depth == 0:
                self._after_close_paren = True

    def _try_split_on_separator(self, char: str) -> bool:
        if self._depth != 0 or char not in {",", ";", "/"}:
            return False
        self._append_current(char)
        self._current = []
        self._after_close_paren = False
        return True

    def _try_implicit_split_after_paren(self, char: str) -> None:
        if self._depth != 0:
            return
        if not self._after_close_paren or char.isspace() or char == ")":
            return
        self._append_current(" ")
        self._current = []
        self._after_close_paren = False

    def _append_current(self, separator: str) -> None:
        part = "".join(self._current).strip()
        if part:
            self._parts.append((part, separator))
