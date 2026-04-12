from scrapers.mixins.apply_for_elements import ApplyForElementsMixin


class StubApplyForElements(ApplyForElementsMixin):
    def __init__(self, table_parser):
        self._table_parser = table_parser


def test_apply_table_parser_to_sections_recurses() -> None:
    class _StubParser:
        def parse(self, data):
            return {"mapped": data["id"]}

    parser = StubApplyForElements(_StubParser())
    payload = {
        "sub_sub_sections": [
            {
                "elements": [{"kind": "table", "data": {"id": "top"}}],
                "sub_sub_sections": [
                    {
                        "elements": [{"kind": "table", "data": {"id": "inner"}}],
                        "sub_sub_sections": [],
                    },
                ],
            },
        ],
    }

    parser._apply_table_parser_to_sections(payload, "sub_sub_sections")

    assert payload["sub_sub_sections"][0]["elements"][0]["data"] == {"mapped": "top"}
    assert payload["sub_sub_sections"][0]["sub_sub_sections"][0]["elements"][0][
        "data"
    ] == {"mapped": "inner"}
