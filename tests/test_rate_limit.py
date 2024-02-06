"""
    tests for rate limit.
"""

import time
from unittest.mock import patch

import pytest

import pytwitter
from pytwitter.error import PyTwitterError
import responses

HEADERS = {
    "x-rate-limit-limit": "300",
    "x-rate-limit-remaining": "299",
    "x-rate-limit-reset": "1612522029",
}
LIMIT_HEADERS = {
    "x-rate-limit-limit": "300",
    "x-rate-limit-remaining": "0",
    "x-rate-limit-reset": int(time.time()) + 60 * 5,
}

USER_URL = "https://api.twitter.com/2/users/2244994945"


class TestRateLimit:
    @staticmethod
    def generate_headers(limit, remaining, reset):
        return {
            "x-rate-limit-limit": f"{limit}",
            "x-rate-limit-remaining": f"{remaining}",
            "x-rate-limit-reset": f"{reset}",
        }

    def test_setter(self):
        rate_limit = pytwitter.RateLimit()
        user_rate_limit = pytwitter.RateLimit(auth_type="user")

        with pytest.raises(PyTwitterError):
            pytwitter.RateLimit(auth_type="others")

        d = rate_limit.set_limit(url=USER_URL, headers=HEADERS)

        assert d.limit == 300
        assert d.remaining == 299

        following_url = "https://api.twitter.com/2/users/123456/following"
        d = user_rate_limit.get_limit(following_url, method="POST")
        assert d.limit == 15

        d = rate_limit.set_limit(
            url="https://api.twitter.com/2/users/123456/following",
            headers=self.generate_headers(15, 10, 1612522029),
        )
        assert d.remaining == 10

    def test_getter(self):
        app_rate_limit = pytwitter.RateLimit()
        assert app_rate_limit.get_limit(url=USER_URL).limit == 300

        user_rate_limit = pytwitter.RateLimit(auth_type="user")
        assert user_rate_limit.get_limit(url=USER_URL).limit == 900

    def test_url_to_resource(self):
        assert pytwitter.RateLimit.url_to_endpoint(USER_URL).resource == "/users/:id"

        other_url = "https://api.twitter.com/2/tests/url"
        assert pytwitter.RateLimit.url_to_endpoint(other_url).resource == "/tests/url"

    @patch("time.sleep")
    @responses.activate
    def test_api_sleep(self, patched_time_sleep, helpers):
        api = pytwitter.Api(bearer_token="bearer token", sleep_on_rate_limit=True)
        user_id = "123456"
        url = f"https://api.twitter.com/2/users/{user_id}"
        users_data = helpers.load_json_data("testdata/apis/user/user_resp.json")
        responses.add(responses.GET, url=url, json=users_data)

        api.rate_limit.set_limit(url=url, headers=LIMIT_HEADERS, method=responses.GET)
        api.get_user(user_id=user_id)
