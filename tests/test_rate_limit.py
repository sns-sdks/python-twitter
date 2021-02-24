"""
    tests for rate limit.
"""
import time
from unittest.mock import patch

import pytwitter
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
    def test_setter(self):
        rate_limit = pytwitter.RateLimit()

        d = rate_limit.set_limit(url=USER_URL, headers=HEADERS)

        assert d.limit == 300
        assert d.remaining == 299

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

        api.rate_limit.set_limit(url=url, headers=LIMIT_HEADERS)
        api.get_user(user_id=user_id)
