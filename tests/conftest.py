import json

import pytest

from pytwitter import Api, StreamApi


class Helpers:
    @staticmethod
    def load_json_data(filename):
        with open(filename, "rb") as f:
            return json.loads(f.read().decode("utf-8"))


@pytest.fixture
def helpers():
    return Helpers


@pytest.fixture
def api():
    return Api(bearer_token="access token")


@pytest.fixture
def api_with_user():
    return Api(
        consumer_key="consumer key",
        consumer_secret="consumer secret",
        access_token="uid-access_token",
        access_secret="access secret",
    )


@pytest.fixture
def stream_api():
    return StreamApi(bearer_token="bearer token")
