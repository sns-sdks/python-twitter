"""
    tests for tweet api
"""

import responses
from pytwitter import Api


@responses.activate
def test_get_tweet(api, helpers):
    tweet_data = helpers.load_json_data("testdata/apis/tweet/tweet_resp.json")
    tweet_id = "1067094924124872705"

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/tweets/{tweet_id}",
        json=tweet_data,
    )

    resp = api.get_tweet(
        tweet_id=tweet_id,
        expansions="attachments.media_keys",
        media_fields=["type", "duration_ms"],
    )
    assert resp.data.id == tweet_id
    assert resp.data.attachments.media_keys[0] == "13_1064638969197977600"
    assert resp.includes.media[0].type == "video"

    resp_json = api.get_tweet(
        tweet_id=tweet_id,
        expansions="attachments.media_keys",
        media_fields=("type", "duration_ms"),
        return_json=True,
    )
    assert resp_json["data"]["id"] == tweet_id
    assert resp_json["data"]["attachments"]["media_keys"][0] == "13_1064638969197977600"
    assert resp_json["includes"]["media"][0]["duration_ms"] == 136637


@responses.activate
def test_get_tweets(api, helpers):
    tweets_data = helpers.load_json_data("testdata/apis/tweet/tweets_resp.json")
    tweet_ids = ["1261326399320715264", "1278347468690915330"]

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/tweets",
        json=tweets_data,
    )

    resp = api.get_tweets(
        tweet_ids=tweet_ids,
        expansions=["author_id"],
        tweet_fields="created_at",
        user_fields=["username", "verified"],
    )
    assert len(resp.data) == 2
    assert resp.data[0].id in tweet_ids
    assert resp.includes.users[0].verified

    resp_json = api.get_tweets(
        tweet_ids="1261326399320715264,1278347468690915330",
        expansions="author_id",
        tweet_fields=["created_at"],
        user_fields="username,verified",
        return_json=True,
    )
    assert resp_json["data"][0]["id"] in tweet_ids
    assert resp_json["includes"]["users"][0]["id"] == "2244994945"


@responses.activate
def test_like_and_unlike_tweet(helpers):
    user_id, tweet_id = "123456", "10987654321"

    api = Api(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        access_token="uid-token",
        access_secret="access secret",
    )

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/users/{user_id}/likes",
        json={"data": {"liked": True}},
    )

    resp = api.like_tweet(user_id=user_id, tweet_id=tweet_id)
    assert resp["data"]["liked"]

    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/users/{user_id}/likes/{tweet_id}",
        json={"data": {"liked": False}},
    )

    resp = api.unlike_tweet(user_id=user_id, tweet_id=tweet_id)
    assert not resp["data"]["liked"]
