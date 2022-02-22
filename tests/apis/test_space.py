"""
    tests for space api
"""

import responses


@responses.activate
def test_get_space(api, helpers):
    space_id = "1DXxyRYNejbKM"

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/spaces/{space_id}",
        json=helpers.load_json_data("testdata/apis/space/space_resp.json"),
    )

    resp = api.get_space(space_id=space_id, space_fields="host_ids")
    assert resp.data.id == space_id


@responses.activate
def test_get_spaces(api, helpers):
    space_ids = ["1DXxyRYNejbKM", "1nAJELYEEPvGL"]

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/spaces",
        json=helpers.load_json_data("testdata/apis/space/spaces_resp.json"),
    )

    resp = api.get_spaces(space_ids=space_ids, space_fields="host_ids")
    assert len(resp.data) == 2
    assert resp.data[0].id == "1DXxyRYNejbKM"


@responses.activate
def test_get_spaces_by_creators(api, helpers):
    creator_ids = ["2244994945", "6253282"]

    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/spaces/by/creator_ids",
        json=helpers.load_json_data("testdata/apis/space/spaces_by_creators.json"),
    )

    resp = api.get_spaces_by_creator(creator_ids=creator_ids, space_fields="host_ids")
    assert len(resp.data) == 2
    assert resp.data[0].id == "1DXxyRYNejbKM"
    assert resp.meta.result_count == 2


@responses.activate
def test_search_spaces(api, helpers):
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/spaces/search",
        json=helpers.load_json_data("testdata/apis/space/spaces_search_resp.json"),
    )

    resp = api.search_spaces(
        query="hello",
        space_fields="title,host_ids",
    )
    assert len(resp.data) == 2
    assert resp.data[0].id == "1DXxyRYNejbKM"
    assert resp.data[0].state == "live"
    assert resp.meta.result_count == 2


@responses.activate
def test_get_buyers_by_space(api, helpers):
    space_id = "1DXxyRYNejbKM"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/spaces/{space_id}/buyers",
        json=helpers.load_json_data("testdata/apis/space/buyers_by_space.json"),
    )

    resp = api.get_buyers_by_space(
        space_id=space_id,
        user_fields="created_at",
        expansions="pinned_tweet_id",
        tweet_fields="created_at",
    )
    assert len(resp.data) == 2
    assert resp.data[0].id == "2244994945"


@responses.activate
def test_get_tweets_by_space(api, helpers):
    space_id = "1DXxyRYNejbKM"
    responses.add(
        responses.GET,
        url=f"https://api.twitter.com/2/spaces/{space_id}/tweets",
        json=helpers.load_json_data("testdata/apis/space/tweets_by_space.json"),
    )

    resp = api.get_tweets_by_space(
        space_id=space_id,
        expansions="author_id",
        user_fields="created_at,description",
    )
    assert len(resp.data) == 3
    assert resp.data[0].id == "1389270063807598594"
