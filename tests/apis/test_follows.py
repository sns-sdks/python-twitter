"""
    tests for follows
"""

import responses


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

    users, includes, meta = resp
    assert len(users) == 5
    assert len(includes.tweets) == 3
    assert meta.result_count == 5


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

    users, includes, meta = resp_json
    assert len(users) == 5
    assert len(includes["tweets"]) == 1
    assert meta["result_count"] == 5
