"""
    tests for follows
"""

import responses

from pytwitter import Api


@responses.activate
def test_get_followings(api, helpers):
    user_id = "2244994945"
    following_data = helpers.load_json_data("testdata/apis/user/following_resp.json")

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}/following",
        json=following_data,
    )

    resp = api.get_following(
        user_id=user_id,
        expansions="pinned_tweet_id",
        max_results=5,
    )

    assert len(resp.data) == 5
    assert len(resp.includes.tweets) == 3
    assert resp.meta.result_count == 5


@responses.activate
def test_get_followers(api, helpers):
    user_id = "2244994945"
    followers_data = helpers.load_json_data("testdata/apis/user/followers_resp.json")

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}/followers",
        json=followers_data,
    )

    resp_json = api.get_followers(
        user_id=user_id,
        expansions="pinned_tweet_id",
        max_results=5,
        return_json=True,
    )

    assert len(resp_json["data"]) == 5
    assert len(resp_json["includes"]["tweets"]) == 1
    assert resp_json["meta"]["result_count"] == 5


@responses.activate
def test_follow_user():
    user_id, target_user_id = "123456", "78910"

    api = Api(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        access_token="access token",
        access_secret="access secret",
    )

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/users/{user_id}/following",
        json={"data": {"following": True, "pending_follow": False}},
    )

    resp = api.follow_user(user_id=user_id, target_user_id=target_user_id)

    assert resp["data"]["following"]


@responses.activate
def test_unfollow_user():
    user_id, target_user_id = "123456", "78910"

    api = Api(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        access_token="access token",
        access_secret="access secret",
    )

    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/users/{user_id}/following/{target_user_id}",
        json={"data": {"following": False}},
    )

    resp = api.unfollow_user(user_id=user_id, target_user_id=target_user_id)

    assert not resp["data"]["following"]
