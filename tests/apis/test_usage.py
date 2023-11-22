"""
    tests for usage api
"""

import responses


@responses.activate
def test_get_usage_tweets(api, helpers):
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/usage/tweets",
        json=helpers.load_json_data("testdata/apis/usage/usage_tweets_resp.json"),
    )

    resp = api.get_usage_tweets()
    assert resp.data.cap_reset_day == 28
