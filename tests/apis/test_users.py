"""
    tests for user api
"""

import pytest
import responses

from pytwitter.error import PyTwitterError


@responses.activate
def test_get_users(api, helpers):
    users_data = helpers.load_json_data("testdata/apis/user/users_resp.json")

    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/users",
        json=users_data,
    )
    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/users/by",
        json=users_data,
    )

    with pytest.raises(PyTwitterError):
        api.get_users()

    ids_resp = api.get_users(
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
    assert len(ids_resp.data) == 2
    assert ids_resp.data[0].verified is True
    assert len(ids_resp.includes.tweets) == 1

    usernames_resp = api.get_users(
        usernames="Twitter,TwitterDev",
        user_fields=(
            "public_metrics,withheld,created_at,description,entities,location,"
            "pinned_tweet_id,profile_image_url,protected,url,verified"
        ),
        expansions="pinned_tweet_id",
        return_json=True,
    )
    assert len(usernames_resp["data"]) == 2
    assert usernames_resp["data"][0]["verified"] is True
    assert len(usernames_resp["includes"]["tweets"]) == 1


@responses.activate
def test_get_user(api, helpers):
    users_data = helpers.load_json_data("testdata/apis/user/user_resp.json")

    user_id = "2244994945"
    username = "TwitterDev"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}",
        json=users_data,
    )
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/by/username/{username}",
        json=users_data,
    )

    with pytest.raises(PyTwitterError):
        api.get_user()

    id_resp = api.get_user(
        user_id=user_id,
        user_fields=["public_metrics", "created_at", "description", "verified"],
    )
    assert id_resp.data.id == user_id
    assert id_resp.data.public_metrics.followers_count == 514020
    assert id_resp.includes is None

    username_resp = api.get_user(
        username=username,
        user_fields="public_metrics,created_at,description,verified",
        return_json=True,
    )
    assert username_resp["data"]["id"] == user_id
    assert username_resp["data"]["verified"] is True
