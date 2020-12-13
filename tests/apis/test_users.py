"""
    tests for user api
"""

import responses


@responses.activate
def test_users_by_ids(api, helpers):
    users_data = helpers.load_json_data("testdata/apis/user/users_by_ids.json")

    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/users",
        json=users_data,
    )

    md_resp = api.users_by_ids(
        ids=["783214", "2244994945"],
        user_fields=(
            "public_metrics",
            "withheld",
            "created_at",
            "description",
            "entities",
            "location",
            "pinned_tweet_id",
            "profile_image_url",
            "protected",
            "url",
            "verified",
        ),
        expansions=["pinned_tweet_id"],
    )
    users, includes = md_resp
    assert len(users) == 2
    assert users[0].verified is True
    assert len(includes.tweets) == 1

    data_resp = api.users_by_ids(
        ids="783214,2244994945",
        user_fields=(
            "public_metrics,withheld,created_at,description,entities,location,"
            "pinned_tweet_id,profile_image_url,protected,url,verified"
        ),
        expansions="pinned_tweet_id",
        return_json=True,
    )
    users, includes = data_resp
    assert len(users) == 2
    assert users[0]["verified"] is True
    assert len(includes["tweets"]) == 1


@responses.activate
def test_user_by_id(api, helpers):
    users_data = helpers.load_json_data("testdata/apis/user/user_by_id.json")

    user_id = "2244994945"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}",
        json=users_data,
    )

    md_resp = api.user_by_id(
        user_id=user_id,
        user_fields=["public_metrics", "created_at", "description", "verified"],
    )
    user, includes = md_resp

    assert user.id == user_id
    assert user.public_metrics.followers_count == 514020
    assert includes is None

    data_resp = api.user_by_id(
        user_id=user_id,
        user_fields="public_metrics,created_at,description,verified",
        return_json=True,
    )
    user, _ = data_resp
    assert user["id"] == user_id
    assert user["verified"] is True
