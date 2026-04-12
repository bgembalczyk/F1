from typing import TypedDict

from models.data.wiki.navbox_link import WikiNavboxLinkData


class WikiNavboxData(TypedDict):
    title: str | None
    links: list[WikiNavboxLinkData]
