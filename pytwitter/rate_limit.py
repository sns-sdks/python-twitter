"""
    Twitter API Rate Limit
"""
import re
from dataclasses import dataclass
from typing import Pattern
from urllib.parse import urlparse

from pytwitter.utils.convertors import conv_type


@dataclass
class RateLimitData:
    limit: int = 15
    remaining: int = 15
    reset: int = 0


@dataclass
class ResourceEndpoint:
    regex: Pattern[str]
    resource: str


USER_ID_SHOW = ResourceEndpoint(re.compile(r"/users/\d+"), "/users/:id")
USER_USERNAME_SHOW = ResourceEndpoint(
    re.compile(r"/users/by/\w+"), "/users/by/:username"
)
USER_ID_FOLLOWING = ResourceEndpoint(
    re.compile(r"/users/\d+/following"), "/users/:id/following"
)
USER_ID_FOLLOWER = ResourceEndpoint(
    re.compile(r"/users/\d+/followers"), "/users/:id/followers"
)
TWEETS_ID_SHOW = ResourceEndpoint(re.compile(r"/tweets/\d+"), "/tweets/:id")

PATH_VAR_ENDPOINTS = [
    USER_ID_SHOW,
    USER_USERNAME_SHOW,
    USER_ID_FOLLOWING,
    USER_ID_FOLLOWER,
    TWEETS_ID_SHOW,
]


class RateLimit:
    """
    API rate limit.
    Refer: https://developer.twitter.com/en/docs/twitter-api/rate-limits
    """

    def __init__(self):
        """
        Stored rate limit data. like:
        ``` json
        {
            "/users/:id": RateLimitData(limit=300, remaining=299, reset=1612522034),
            "/users/by/:username": RateLimitData(limit=300, remaining=289, reset=1612522029),
        }
        ```
        """
        self.mapping = {}

    @staticmethod
    def url_to_resource(url):
        resource = urlparse(url).path.replace("/2", "", 1)  # only replace api version
        for endpoint in PATH_VAR_ENDPOINTS:
            if re.fullmatch(endpoint.regex, resource):
                return endpoint.resource
        return resource

    def set_limit(self, url, headers):
        """
        Twitter API rate limit data stored at requests headers. Like:

        ``` json
        {
            "x-rate-limit-limit": "300",
            "x-rate-limit-remaining": "299",
            "x-rate-limit-reset": "1612519043",
        }
        ```

        :param url: api query url.
        :param headers: api response headers.
        :return:
        """
        endpoint = self.url_to_resource(url=url)
        data = {
            "limit": conv_type("limit", int, headers.get("x-rate-limit-limit", 0)),
            "remaining": conv_type(
                "remaining", int, headers.get("x-rate-limit-remaining", 0)
            ),
            "reset": conv_type("reset", int, headers.get("x-rate-limit-reset", 0)),
        }
        self.mapping[endpoint] = RateLimitData(**data)

        return self.get_limit(url=url)

    def get_limit(self, url):
        endpoint = self.url_to_resource(url=url)
        if endpoint not in self.mapping:
            return RateLimitData()

        return self.mapping[endpoint]
