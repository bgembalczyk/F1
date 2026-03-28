import re

GRAND_PRIX_KEYWORD = "grand prix"
GRAND_PRIX_NAVBOX_TEMPLATE = "Template:Formula_One_Grands_Prix"

SHORT_HEX_LEN = 3
BACKGROUND_HEX = re.compile(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})")
BACKGROUND_MAP = {
    "ffffcc": "pre_war_european_championship",
    "d0ffb0": "pre_war_world_manufacturers_championship",
    "ffcccc": "non_championship",
}
DEFAULT_CHAMPIONSHIP = "formula_one_world_championship"
UNKNOWN_CHAMPIONSHIP = "unknown"
