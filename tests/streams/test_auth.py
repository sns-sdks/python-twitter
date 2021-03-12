"""
    Stream Auth tests.
"""

import pytest
import responses

from pytwitter import StreamApi, PyTwitterError


@responses.activate
def test_initial_api(helpers):
    # test with not auth
    with pytest.raises(PyTwitterError):
        StreamApi()

    api = StreamApi(bearer_token="bearer token")

    token_data = helpers.load_json_data("testdata/apis/authflow/bearer_token.json")
    responses.add(
        responses.POST, url="https://api.twitter.com/oauth2/token", json=token_data
    )

    api = StreamApi(consumer_key="consumer key", consumer_secret="consumer secret")


@responses.activate
def test_generate_token():

    responses.add(
        responses.POST,
        url="https://api.twitter.com/oauth2/token",
        json={
            "errors": [
                {
                    "code": 99,
                    "message": "Unable to verify your credentials",
                    "label": "authenticity_token_error",
                }
            ]
        },
        status=403,
    )

    with pytest.raises(PyTwitterError):
        StreamApi(consumer_key="error", consumer_secret="error")
