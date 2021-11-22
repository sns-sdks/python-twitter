"""
    tests for user api
"""

import responses


@responses.activate
def test_get_list(api, helpers):
    list_id = "84839422"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/lists/{list_id}",
        json=helpers.load_json_data("testdata/apis/lists/list_resp.json"),
    )

    resp = api.get_list(list_id=list_id)
    assert resp.data.id == list_id


@responses.activate
def test_get_user_owned_lists(api, helpers):
    user_id = "2244994945"

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}/owned_lists",
        json=helpers.load_json_data("testdata/apis/lists/user_lists_resp.json"),
    )

    resp = api.get_user_owned_lists(
        user_id=user_id,
        list_fields="follower_count",
        expansions="owner_id",
        user_fields="created_at",
    )
    assert resp.data[0].id == "1451305624956858369"
    assert resp.meta.result_count == 1


@responses.activate
def test_create_list(api_with_user, helpers):
    responses.add(
        responses.POST,
        url="https://api.twitter.com/2/lists",
        json={"data": {"id": "1441162269824405510", "name": "test v2 create list"}},
    )

    my_list = api_with_user.create_list(
        name="test v2 create list", description="test v2 create list", private=False
    )
    assert my_list.id == "1441162269824405510"

    my_list_json = api_with_user.create_list(
        name="test v2 create list", return_json=True
    )
    assert my_list_json["data"]["id"] == "1441162269824405510"


@responses.activate
def test_update_list(api_with_user, helpers):
    list_id = "1441162269824405510"
    responses.add(
        responses.PUT,
        url=f"https://api.twitter.com/2/lists/{list_id}",
        json={"data": {"updated": True}},
    )

    update = api_with_user.update_list(
        list_id,
        name="test v2 update list",
        description="list description",
        private=False,
    )
    assert update["data"]["updated"]


@responses.activate
def test_delete_list(api_with_user, helpers):
    list_id = "1441162269824405510"
    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/lists/{list_id}",
        json={"data": {"deleted": True}},
    )

    deleted = api_with_user.delete_list(list_id=list_id)
    assert deleted["data"]["deleted"]


@responses.activate
def test_get_list_tweets(api, helpers):
    list_id = "84839422"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/lists/{list_id}/tweets",
        json=helpers.load_json_data("testdata/apis/lists/list_tweets_resp.json"),
    )

    resp = api.get_lists_tweets(
        list_id=list_id, expansions="author_id", user_fields="verified"
    )
    assert resp.data[0].id == "1067094924124872705"
    assert resp.meta.result_count == 1


@responses.activate
def test_get_list_members(api, helpers):
    list_id = "84839422"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/lists/{list_id}/members",
        json=helpers.load_json_data("testdata/apis/lists/list_members_resp.json"),
    )

    resp = api.get_list_members(
        list_id=list_id,
        expansions="pinned_tweet_id",
        user_fields="username",
        max_results=5,
    )
    assert resp.data[0].id == "1319036828964454402"
    assert resp.meta.result_count == 5


@responses.activate
def test_get_user_memberships_lists(api, helpers):
    user_id = "84839422"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/users/{user_id}/list_memberships",
        json=helpers.load_json_data(
            "testdata/apis/lists/user_memberships_lists_resp.json"
        ),
    )

    resp = api.get_user_memberships_lists(
        user_id=user_id,
        list_fields="follower_count",
        expansions="owner_id",
        user_fields="created_at",
    )
    assert resp.data[0].id == "1451951974291689472"
    assert resp.meta.result_count == 1


@responses.activate
def test_add_member_to_list(api_with_user, helpers):
    list_id = "1441162269824405510"
    user_id = "2244994945"
    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/lists/{list_id}/members",
        json={"data": {"is_member": True}},
    )

    is_member = api_with_user.add_list_member(list_id=list_id, user_id=user_id)
    assert is_member["data"]["is_member"]


@responses.activate
def test_remove_member_to_list(api_with_user, helpers):
    list_id = "1441162269824405510"
    user_id = "2244994945"
    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/lists/{list_id}/members/{user_id}",
        json={"data": {"is_member": False}},
    )

    is_member = api_with_user.remove_list_member(list_id=list_id, user_id=user_id)
    assert not is_member["data"]["is_member"]


@responses.activate
def test_follow_list(api_with_user, helpers):
    list_id = "1441162269824405510"
    user_id = "2244994945"
    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/users/{user_id}/followed_lists",
        json={"data": {"following": True}},
    )

    following = api_with_user.follow_list(user_id=user_id, list_id=list_id)
    assert following["data"]["following"]


@responses.activate
def test_unfollow_list(api_with_user, helpers):
    list_id = "1441162269824405510"
    user_id = "2244994945"
    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/users/{user_id}/followed_lists/{list_id}",
        json={"data": {"following": False}},
    )

    following = api_with_user.unfollow_list(user_id=user_id, list_id=list_id)
    assert not following["data"]["following"]


@responses.activate
def test_pin_list(api_with_user, helpers):
    list_id = "1441162269824405510"
    user_id = "2244994945"
    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/users/{user_id}/pinned_lists",
        json={"data": {"pinned": True}},
    )

    following = api_with_user.pin_list(user_id=user_id, list_id=list_id)
    assert following["data"]["pinned"]


@responses.activate
def test_unpin_list(api_with_user, helpers):
    list_id = "1441162269824405510"
    user_id = "2244994945"
    responses.add(
        responses.DELETE,
        url=f"https://api.twitter.com/2/users/{user_id}/pinned_lists/{list_id}",
        json={"data": {"pinned": False}},
    )

    following = api_with_user.unpin_list(user_id=user_id, list_id=list_id)
    assert not following["data"]["pinned"]
