"""
    tests for user api
"""

import responses


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

    deleted = api_with_user.delete_list(list_id)
    assert deleted["data"]["deleted"]


@responses.activate
def test_add_member_to_list(api_with_user, helpers):
    list_id = "1441162269824405510"
    user_id = "2244994945"
    responses.add(
        responses.POST,
        url=f"https://api.twitter.com/2/lists/{list_id}/members",
        json={"data": {"is_member": True}},
    )

    is_member = api_with_user.add_list_member(list_id, user_id)
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

    is_member = api_with_user.remove_list_member(list_id, user_id)
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

    following = api_with_user.follow_list(user_id, list_id)
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

    following = api_with_user.unfollow_list(user_id, list_id)
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

    following = api_with_user.pin_list(user_id, list_id)
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

    following = api_with_user.unpin_list(user_id, list_id)
    assert not following["data"]["pinned"]
