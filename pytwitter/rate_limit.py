"""
    Twitter API Rate Limit
"""
import re
from dataclasses import dataclass
from typing import Optional, Pattern
from urllib.parse import urlparse

from pytwitter.utils.convertors import conv_type


@dataclass
class RateLimitData:
    limit: int = 15
    remaining: int = 15
    reset: int = 0


@dataclass
class Endpoint:
    resource: str
    regex: Optional[Pattern[str]] = None
    app_limit: int = 15
    user_limit: int = 15

    def get_limit(self, auth_type):
        if auth_type == "user":
            return self.user_limit
        return self.app_limit


USER_ID_SHOW = Endpoint(
    resource="/users/:id",
    regex=re.compile(r"/users/\d+"),
    app_limit=300,
    user_limit=900,
)
USER_USERNAME_SHOW = Endpoint(
    resource="/users/by/:username",
    regex=re.compile(r"/users/by/\w+"),
    app_limit=300,
    user_limit=900,
)
USER_ID_FOLLOWING = Endpoint(
    resource="/users/:id/following", regex=re.compile(r"/users/\d+/following")
)
USER_ID_FOLLOWER = Endpoint(
    resource="/users/:id/followers", regex=re.compile(r"/users/\d+/followers")
)
USER_ID_TIMELINE = Endpoint(
    resource="/users/:id/tweets",
    regex=re.compile(r"/users/\d+/tweets"),
    app_limit=1500,
    user_limit=900,
)
USER_ID_MENTIONS = Endpoint(
    resource="/users/:id/mentions",
    regex=re.compile(r"/users/\d+/mentions"),
    app_limit=450,
    user_limit=180,
)
TWEETS_ID_SHOW = Endpoint(
    resource="/tweets/:id",
    regex=re.compile(r"/tweets/\d+"),
    app_limit=300,
    user_limit=900,
)
TWEETS_ID_HIDDEN = Endpoint(
    resource="/tweets/:id/hidden",
    regex=re.compile(r"/tweets/\d+/hidden"),
    app_limit=0,
    user_limit=50,
)

PATH_VAR_ENDPOINTS = [
    USER_ID_SHOW,
    USER_USERNAME_SHOW,
    USER_ID_FOLLOWING,
    USER_ID_FOLLOWER,
    USER_ID_TIMELINE,
    USER_ID_MENTIONS,
    TWEETS_ID_SHOW,
    TWEETS_ID_HIDDEN,
]


class RateLimit:
    """
    API rate limit.
    Refer: https://developer.twitter.com/en/docs/twitter-api/rate-limits
    """

    def __init__(self, auth_type="app"):
        """
        Stored rate limit data. like:
        ``` json
        {
            "/users/:id": RateLimitData(limit=300, remaining=299, reset=1612522034),
            "/users/by/:username": RateLimitData(limit=300, remaining=289, reset=1612522029),
        }
        ```
        :param auth_type: app auth or user auth
        """
        self.auth_type = auth_type
        self.mapping = {}

    @staticmethod
    def url_to_endpoint(url) -> Endpoint:
        resource = urlparse(url).path.replace("/2", "", 1)  # only replace api version
        for endpoint in PATH_VAR_ENDPOINTS:
            if re.fullmatch(endpoint.regex, resource):
                return endpoint
        return Endpoint(resource=resource)

    def set_limit(self, url, headers) -> RateLimitData:
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
        endpoint = self.url_to_endpoint(url=url)
        data = {
            "limit": conv_type("limit", int, headers.get("x-rate-limit-limit", 0)),
            "remaining": conv_type(
                "remaining", int, headers.get("x-rate-limit-remaining", 0)
            ),
            "reset": conv_type("reset", int, headers.get("x-rate-limit-reset", 0)),
        }
        self.mapping[endpoint.resource] = RateLimitData(**data)

        return self.get_limit(url=url)

    def get_limit(self, url) -> RateLimitData:
        endpoint = self.url_to_endpoint(url=url)
        if endpoint.resource not in self.mapping:
            limit = endpoint.get_limit(auth_type=self.auth_type)
            return RateLimitData(limit=limit, remaining=limit)

        return self.mapping[endpoint.resource]
