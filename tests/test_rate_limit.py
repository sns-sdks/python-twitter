"""
    tests for rate limit.
"""
import pytwitter

HEADERS = {
    "x-rate-limit-limit": "300",
    "x-rate-limit-remaining": "299",
    "x-rate-limit-reset": "1612522029",
}

USER_URL = "https://api.twitter.com/2/users/2244994945"


class TestRateLimit:
    def test_setter(self):
        rate_limit = pytwitter.RateLimit()

        d = rate_limit.set_limit(url=USER_URL, headers=HEADERS)

        assert d.limit == 300
        assert d.remaining == 299

    def test_getter(self):
        rate_limit = pytwitter.RateLimit()
        d = rate_limit.get_limit(url=USER_URL)

        assert d.limit == 15

    def test_url_to_resource(self):
        assert pytwitter.RateLimit.url_to_resource(USER_URL) == "/users/:id"

        other_url = "https://api.twitter.com/2/tests/url"
        assert pytwitter.RateLimit.url_to_resource(other_url) == "/tests/url"
