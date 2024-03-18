"""
    tests for the trends api
"""

import responses


@responses.activate
def test_get_trends_by_woeid(api, helpers):
    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/trends/by/woeid/1",
        json=helpers.load_json_data("testdata/apis/trends/trends_resp.json"),
    )

    resp = api.get_trends_by_woeid(1)
    assert resp.data[0].trend_name == "#TEZOSTUESDAY"
