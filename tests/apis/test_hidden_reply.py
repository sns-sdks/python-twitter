"""
    tests for hide reply
"""

import responses

from pytwitter import Api


@responses.activate
def test_hidden_reply():
    tweet_id = "123456"

    api = Api(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        access_token="uid-token",
        access_secret="access secret",
    )

    responses.add(
        responses.PUT,
        url=f"https://api.twitter.com/2/tweets/{tweet_id}/hidden",
        json={"data": {"hidden": True}},
    )

    hide_resp = api.hidden_reply(tweet_id=tweet_id)
    assert hide_resp["data"]["hidden"]


@responses.activate
def test_unhide_reply():
    tweet_id = "123456"

    api = Api(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        access_token="uid-token",
        access_secret="access secret",
    )

    responses.add(
        responses.PUT,
        url=f"https://api.twitter.com/2/tweets/{tweet_id}/hidden",
        json={"data": {"hidden": False}},
    )
    hide_resp = api.hidden_reply(tweet_id=tweet_id, hidden=False)
    assert not hide_resp["data"]["hidden"]
