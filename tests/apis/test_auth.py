"""
    tests for auth
"""

import responses
from pytwitter import Api


@responses.activate
def test_generate_bearer_token(api, helpers):
    token_data = helpers.load_json_data("testdata/apis/authflow/bearer_token.json")

    responses.add(
        responses.POST, url="https://api.twitter.com/oauth2/token", json=token_data
    )

    # test initial by app
    Api(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        application_only_auth=True,
    )

    # test generate by hand
    resp = api.generate_bearer_token(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
    )
    assert (
        resp["access_token"]
        == "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA%2FAAAAAAAAAAAAAAAAAAAA%3DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    )


@responses.activate
def test_invalidate_bearer_token(api, helpers):
    bearer_token = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA%2FAAAAAAAAAAAAAAAAAAAA%3DAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    token_data = helpers.load_json_data("testdata/apis/authflow/invalidate_token.json")

    responses.add(
        responses.POST,
        url="https://api.twitter.com/oauth2/invalidate_token",
        json=token_data,
    )

    resp = api.invalidate_bearer_token(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        access_token=bearer_token,
    )

    assert resp["access_token"] == bearer_token
