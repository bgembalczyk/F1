from __future__ import annotations

from html.parser import HTMLParser
from typing import Any, Iterable, List, Optional


class Tag:
    def __init__(self, name: str, attrs: Optional[dict[str, Any]] = None, parent: "Tag" | None = None):
        self.name = name
        self.attrs = attrs or {}
        self.children: List[Any] = []
        self.parent = parent
        self.root: Tag = parent.root if parent else self

    def append_child(self, child: Any) -> None:
        self.children.append(child)
        if isinstance(child, Tag):
            child.parent = self
            child.root = self.root

    def get(self, key: str, default: Any = None) -> Any:
        if key == "class" and "class" in self.attrs:
            classes = self.attrs.get("class")
            if isinstance(classes, str):
                return classes.split()
            return classes
        return self.attrs.get(key, default)

    def get_text(self, separator: str | None = "", strip: bool = False) -> str:
        parts: List[str] = []
        for child in self.children:
            if isinstance(child, Tag):
                parts.append(child.get_text(separator, strip))
            else:
                parts.append(str(child))
        text = separator.join(parts) if separator is not None else "".join(parts)
        if strip:
            text = text.strip()
        return text

    def _matches_name(self, name: Any) -> bool:
        if name is None:
            return True
        if isinstance(name, (list, tuple, set)):
            return self.name in name
        return self.name == name

    def _matches_class(self, class_: Any) -> bool:
        if class_ is None:
            return True
        classes = self.get("class") or []
        if isinstance(class_, str):
            return class_ in classes
        return any(cls in classes for cls in class_)

    def _iter_tags(self) -> Iterable["Tag"]:
        yield self
        for child in self.children:
            if isinstance(child, Tag):
                yield from child._iter_tags()

    def find(self, name: Any = None, id: str | None = None, class_: Any = None):
        for child in self._iter_tags():
            if child is self:
                continue
            if id is not None and child.get("id") != id:
                continue
            if not child._matches_name(name):
                continue
            if not child._matches_class(class_):
                continue
            return child
        return None

    def find_all(self, name: Any = None, class_: Any = None, href: Any = False) -> List["Tag"]:
        results: List[Tag] = []
        for child in self._iter_tags():
            if child is self:
                continue
            if not child._matches_name(name):
                continue
            if not child._matches_class(class_):
                continue
            if href is not False:
                if href is True and not child.get("href"):
                    continue
            results.append(child)
        return results

    def find_all_next(self, name: Any = None, class_: Any = None) -> List["Tag"]:
        tags = list(self.root._iter_tags())
        try:
            start = tags.index(self)
        except ValueError:
            return []
        results: List[Tag] = []
        for child in tags[start + 1 :]:
            if not child._matches_name(name):
                continue
            if not child._matches_class(class_):
                continue
            results.append(child)
        return results

    def decompose(self) -> None:
        if self.parent and self in self.parent.children:
            self.parent.children.remove(self)


class _SoupParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.root = Tag("[document]")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]):
        attr_dict = {k: (v if v is not None else "") for k, v in attrs}
        element = Tag(tag, attr_dict, parent=self.stack[-1])
        self.stack[-1].append_child(element)
        self.stack.append(element)

    def handle_endtag(self, tag: str):
        if len(self.stack) > 1:
            self.stack.pop()

    def handle_data(self, data: str):
        if data:
            self.stack[-1].append_child(data)


class BeautifulSoup(Tag):
    def __init__(self, html: str, parser: str | None = None):
        self.parser = _SoupParser()
        self.parser.feed(html)
        root = self.parser.root
        super().__init__(root.name, root.attrs)
        self.children = root.children
        for child in self.children:
            if isinstance(child, Tag):
                child.parent = self
                child.root = self

