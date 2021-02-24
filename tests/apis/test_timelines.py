"""
    tests for timelines
"""

import responses


@responses.activate
def test_get_timelines(api, helpers):
    user_id = "2244994945"
    timelines_data = helpers.load_json_data(
        "testdata/apis/timeline/timeline_tweets.json"
    )

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}/tweets",
        json=timelines_data,
    )

    resp = api.get_timelines(
        user_id=user_id,
        tweet_fields=["id", "text", "created_at", "public_metrics"],
        exclude=["retweets", "replies"],
        max_results=5,
    )

    assert len(resp.data) == 5
    assert resp.data[0].public_metrics.retweet_count == 10
    assert resp.meta.newest_id == "1364275610764201984"


@responses.activate
def test_get_mentions(api, helpers):
    user_id = "2244994945"
    mentions_data = helpers.load_json_data(
        "testdata/apis/timeline/timeline_mentions.json"
    )

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}/mentions",
        json=mentions_data,
    )

    resp = api.get_mentions(
        user_id=user_id,
        tweet_fields=["id", "text", "created_at", "public_metrics"],
        max_results=5,
    )

    assert len(resp.data) == 5
    assert resp.data[0].public_metrics.reply_count == 0
    assert resp.meta.newest_id == "1364398068313903104"
