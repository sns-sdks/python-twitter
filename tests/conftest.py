import json

import pytest


class Helpers:
    @staticmethod
    def load_json_data(filename):
        with open(filename, "rb") as f:
            return json.loads(f.read().decode("utf-8"))


@pytest.fixture
def helpers():
    return Helpers
