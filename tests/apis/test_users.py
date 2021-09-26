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
    assert ids_resp.data[0].verified
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
    assert username_resp["data"]["verified"]


@responses.activate
def test_block_and_unblock_user(api_with_user):
    user_id, target_user_id = "123456", "78910"

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/users/{user_id}/blocking",
        json={"data": {"blocking": True}},
    )

    resp = api_with_user.block_user(user_id=user_id, target_user_id=target_user_id)
    assert resp["data"]["blocking"]

    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/users/{user_id}/blocking/{target_user_id}",
        json={"data": {"blocking": False}},
    )

    resp = api_with_user.unblock_user(user_id=user_id, target_user_id=target_user_id)
    assert not resp["data"]["blocking"]


@responses.activate
def test_get_blocking_users(api_with_user, helpers):
    users_data = helpers.load_json_data(
        "testdata/apis/user/blocking_users_list_resp.json"
    )

    user_id = "2244994945"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}/blocking",
        json=users_data,
    )

    users_resp = api_with_user.get_blocking_users(
        user_id=user_id,
        expansions=["pinned_tweet_id"],
        user_fields=["id", "created_at", "description"],
    )
    assert users_resp.data[0].id == "1065249714214457345"
    assert users_resp.data[0].created_at == "2018-11-21T14:24:58.000Z"
    assert users_resp.includes.tweets[0].id == "1389270063807598594"

    users_json_resp = api_with_user.get_blocking_users(
        user_id=user_id,
        expansions="pinned_tweet_id",
        user_fields="id,created_at,description",
        return_json=True,
    )
    assert users_json_resp["data"][0]["id"] == "1065249714214457345"
    assert users_json_resp["includes"]["tweets"][0]["id"] == "1389270063807598594"


@responses.activate
def test_get_user_liked_tweets(api_with_user, helpers):
    tweets_data = helpers.load_json_data(
        "testdata/apis/user/user_liked_tweets_resp.json"
    )
    user_id = "1301152652357595137"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}/liked_tweets",
        json=tweets_data,
    )

    users_resp = api_with_user.get_user_liked_tweets(
        user_id=user_id,
        expansions=["pinned_tweet_id"],
        user_fields=["id", "created_at"],
        tweet_fields=["created_at"],
    )
    assert users_resp.data[0].id == "1395474683630399500"
    assert users_resp.includes.users[0].id == "15772978"

    users_json_resp = api_with_user.get_user_liked_tweets(
        user_id=user_id,
        expansions="pinned_tweet_id",
        user_fields="id,created_at",
        tweet_fields="created_at",
        return_json=True,
    )
    assert users_json_resp["data"][0]["id"] == "1395474683630399500"
    assert users_json_resp["includes"]["users"][0]["id"] == "15772978"


@responses.activate
def test_get_muting(api_with_user, helpers):
    muting_data = helpers.load_json_data("testdata/apis/user/muting_resp.json")
    user_id = "1324848235714736129"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}/muting",
        json=muting_data,
    )

    users_resp = api_with_user.get_user_muting(
        user_id=user_id,
        expansions=["pinned_tweet_id"],
        user_fields=["id", "created_at"],
        tweet_fields=["created_at"],
    )
    assert users_resp.data[0].id == "2244994945"
    assert users_resp.includes.tweets[0].id == "1430984356139470849"

    users_resp_json = api_with_user.get_user_muting(
        user_id=user_id,
        expansions=["pinned_tweet_id"],
        user_fields=["id", "created_at"],
        tweet_fields=["created_at"],
        return_json=True,
    )
    assert users_resp_json["data"][0]["id"] == "2244994945"
    assert users_resp_json["includes"]["tweets"][0]["id"] == "1430984356139470849"


@responses.activate
def test_mute_and_unmute_user(api_with_user):
    user_id, target_user_id = "123456", "78910"

    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/users/{user_id}/muting",
        json={"data": {"muting": True}},
    )

    resp = api_with_user.mute_user(user_id=user_id, target_user_id=target_user_id)
    assert resp["data"]["muting"]

    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/users/{user_id}/muting/{target_user_id}",
        json={"data": {"muting": False}},
    )

    resp = api_with_user.unmute_user(user_id=user_id, target_user_id=target_user_id)
    assert not resp["data"]["muting"]
