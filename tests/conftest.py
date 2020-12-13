import json

import pytest

from pytwitter import Api


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
