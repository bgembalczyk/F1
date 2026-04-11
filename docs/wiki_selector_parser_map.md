# Wiki element selector map

Krótka mapa odpowiedzialności warstwy `scrapers/parsers/wiki/element.py`.

| Selector (tag + class/id) | Parser elementowy | Typ wyniku (`kind`) |
|---|---|---|
| `table.wikitable` | `WikiTableParser` | `table` |
| `ul`, `ol` | `WikiListParser` | `list` |
| `table.infobox` | `WikiInfoboxParser` | `infobox` |
| `div.mw-heading2`, `div.mw-heading3`, `div.mw-heading4` | parser sekcji przekazany do registry (`section_parser`) | `section` |
| `figure` | `WikiFigureParser` | `figure` |
| `p` | `WikiParagraphParser` | `paragraph` |
| `div.navbox` | `WikiNavboxParser` | `navbox` |
| `div.reflist` | `ReferencesWrapParser` | `references_wrap` |
| `div[class*="references-wrap"]` | `ReferencesWrapParser` | `references_wrap` |
