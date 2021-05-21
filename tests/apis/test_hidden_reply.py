"""
    tests for hide reply
"""

import responses


@responses.activate
def test_hidden_reply(api_with_user):
    tweet_id = "123456"

    responses.add(
        responses.PUT,
        url=f"https://api.twitter.com/2/tweets/{tweet_id}/hidden",
        json={"data": {"hidden": True}},
    )

    hide_resp = api_with_user.hidden_reply(tweet_id=tweet_id)
    assert hide_resp["data"]["hidden"]


@responses.activate
def test_unhide_reply(api_with_user):
    tweet_id = "123456"

    responses.add(
        responses.PUT,
        url=f"https://api.twitter.com/2/tweets/{tweet_id}/hidden",
        json={"data": {"hidden": False}},
    )
    hide_resp = api_with_user.hidden_reply(tweet_id=tweet_id, hidden=False)
    assert not hide_resp["data"]["hidden"]
