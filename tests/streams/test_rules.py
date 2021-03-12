"""
    Stream rules tests.
"""

import pytest
import responses

from pytwitter import PyTwitterError


@responses.activate
def test_get_rules(stream_api, helpers):
    rules_data = helpers.load_json_data("testdata/streams/get_rules.json")

    responses.add(
        responses.GET,
        url="https://api.twitter.com/2/tweets/search/stream/rules",
        json=rules_data,
    )

    resp = stream_api.get_rules(ids=["1165037377523306497", "1165037377523306498"])

    assert resp.meta.sent == "2019-08-29T01:12:10.729Z"
    assert len(resp.data) == 2
    assert resp.data[0].id == "1165037377523306497"

    resp_json = stream_api.get_rules(return_json=True)
    assert len(resp_json["data"]) == 2


@responses.activate
def test_manage_rules(stream_api, helpers):
    add_rules_data = helpers.load_json_data("testdata/streams/post_rules.json")
    delete_rules_data = helpers.load_json_data("testdata/streams/delete_rules.json")
    delete_error_data = helpers.load_json_data("testdata/streams/delete_error.json")

    # add rules
    responses.add(
        responses.POST,
        url="https://api.twitter.com/2/tweets/search/stream/rules",
        json=add_rules_data,
        status=201,
    )
    responses.add(
        responses.POST,
        url="https://api.twitter.com/2/tweets/search/stream/rules",
        json=delete_rules_data,
        status=200,
    )
    responses.add(
        responses.POST,
        url="https://api.twitter.com/2/tweets/search/stream/rules",
        json=delete_error_data,
        status=400,
    )
    responses.add(
        responses.POST,
        url="https://api.twitter.com/2/tweets/search/stream/rules",
        json=None,
        status=200,
    )

    resp = stream_api.manage_rules(
        rules={
            "add": [
                {"value": "cat has:media", "tag": "cats with media"},
                {"value": "cat has:media -grumpy", "tag": "happy cats with media"},
                {"value": "meme", "tag": "funny things"},
                {"value": "meme has:images"},
            ]
        },
    )
    assert resp.meta.summary.created == 4

    # delete rules
    resp_json = stream_api.manage_rules(
        rules={"delete": {"ids": ["1165037377523306498", "1165037377523306499"]}},
        return_json=True,
    )
    assert resp_json["meta"]["summary"]["deleted"] == 1

    with pytest.raises(PyTwitterError):
        stream_api.manage_rules(
            rules={"delete": {"ids": ["1165037377523306498", "1165037377523306499"]}},
        )

    with pytest.raises(PyTwitterError):
        stream_api.manage_rules(
            rules={"delete": {"ids": ["1165037377523306499"]}},
        )
