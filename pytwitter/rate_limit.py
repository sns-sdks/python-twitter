"""
    Twitter API Rate Limit.

    Refer: https://developer.twitter.com/en/docs/twitter-api/rate-limits
"""
import logging
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, Pattern
from urllib.parse import urlparse

from pytwitter.error import PyTwitterError
from pytwitter.utils.convertors import conv_type

logger = logging.getLogger(__name__)


@dataclass
class RateLimitData:
    limit: int = 15
    remaining: int = 15
    reset: int = 0


@dataclass
class Endpoint:
    resource: str
    regex: Optional[Pattern[str]] = None

    # For different auth type and endpoint
    LIMIT_APP_GET: int = 15
    LIMIT_USER_GET: int = 15
    LIMIT_APP_POST: int = 0
    LIMIT_USER_POST: int = 0
    LIMIT_USER_PUT: int = 0
    LIMIT_USER_DELETE: int = 0

    def get_limit(self, auth_type, method="GET"):
        return getattr(self, f"LIMIT_{auth_type.upper()}_{method}", 0)


TWEETS_BY_ID = Endpoint(
    resource="/tweets",
    regex=re.compile(r"/tweets"),
    LIMIT_APP_GET=300,
    LIMIT_USER_GET=900,
    LIMIT_USER_POST=200,
)
TWEET_BY_ID = Endpoint(
    resource="/tweets/:id",
    regex=re.compile(r"/tweets/\d+"),
    LIMIT_APP_GET=300,
    LIMIT_USER_GET=900,
    LIMIT_USER_DELETE=50,
)
USER_TIMELINE = Endpoint(
    resource="/users/:id/tweets",
    regex=re.compile(r"/users/\d+/tweets"),
    LIMIT_APP_GET=1500,
    LIMIT_USER_GET=900,
)
USER_TIMELINE_REVERSE = Endpoint(
    resource="/users/:id/timelines/reverse_chronological",
    regex=re.compile(r"/users/\d+/timelines/reverse_chronological"),
    LIMIT_USER_GET=180,
)
USER_MENTIONS = Endpoint(
    resource="/users/:id/mentions",
    regex=re.compile(r"/users/\d+/mentions"),
    LIMIT_APP_GET=450,
    LIMIT_USER_GET=180,
)
TWEET_SEARCH_RECENT = Endpoint(
    resource="/tweets/search/recent",
    regex=re.compile(r"/tweets/search/recent"),
    LIMIT_APP_GET=450,
    LIMIT_USER_GET=180,
)
TWEET_SEARCH_ALL = Endpoint(
    resource="/tweets/search/all",
    regex=re.compile(r"/tweets/search/all"),
    LIMIT_APP_GET=300,
)
TWEET_COUNTS = Endpoint(
    resource="/tweets/counts",
    regex=re.compile(r"/tweets/counts/\w+"),
    LIMIT_APP_GET=300,
)
TWEET_RETWEET_USER = Endpoint(
    resource="/tweets/:id/retweeted_by",
    regex=re.compile(r"/tweets/\d+/retweeted_by"),
    LIMIT_APP_GET=75,
    LIMIT_USER_GET=75,
)
TWEET_QUOTE_TWEETS = Endpoint(
    resource="/tweets/:id/quote_tweets",
    regex=re.compile(r"/tweets/\d+/quote_tweets"),
    LIMIT_USER_GET=75,
    LIMIT_APP_GET=75,
)
USER_TWEET_RETWEET = Endpoint(
    resource="/users/:id/retweets",
    regex=re.compile(r"/users/\d+/retweets"),
    LIMIT_USER_POST=50,
)
USER_TWEET_RETWEET_REMOVE = Endpoint(
    resource="/users/:id/retweets/:tweet_id",
    regex=re.compile(r"/users/\d+/retweets/\d+"),
    LIMIT_USER_POST=50,
)
TWEET_LIKING_USER = Endpoint(
    resource="/tweets/:id/liking_users",
    regex=re.compile(r"/tweets/\d+/liking_users"),
    LIMIT_APP_GET=75,
    LIMIT_USER_GET=75,
)
USER_LIKED_TWEET = Endpoint(
    resource="/users/:id/liked_tweets",
    regex=re.compile(r"/users/\d+/liked_tweets"),
    LIMIT_APP_GET=75,
    LIMIT_USER_GET=75,
)
USER_TWEET_LIKE = Endpoint(
    resource="/users/:id/likes",
    regex=re.compile(r"/users/\d+/likes"),
    LIMIT_USER_POST=50,
)
USER_TWEET_LIKE_REMOVE = Endpoint(
    resource="/users/:id/likes/:tweet_id",
    regex=re.compile(r"/users/\d+/likes/\d+"),
    LIMIT_USER_POST=50,
)
USER_BOOKMARK_TWEET = Endpoint(
    resource="/users/:id/bookmarks",
    regex=re.compile(r"/users/\d+/bookmarks"),
    LIMIT_USER_GET=180,
    LIMIT_USER_POST=50,
)
USER_BOOKMARK_TWEET_REMOVE = Endpoint(
    resource="/users/:id/bookmarks/:tweet_id",
    regex=re.compile(r"/users/\d+/bookmarks/\d+"),
    LIMIT_USER_DELETE=50,
)
TWEET_HIDDEN = Endpoint(
    resource="/tweets/:id/hidden",
    regex=re.compile(r"/tweets/\d+/hidden"),
    LIMIT_USER_PUT=50,
)

USER_BY_ID = Endpoint(
    resource="/users/:id",
    regex=re.compile(r"/users/\d+"),
    LIMIT_APP_GET=300,
    LIMIT_USER_GET=900,
)
USERS_BY_ID = Endpoint(
    resource="/users",
    regex=re.compile(r"/users"),
    LIMIT_APP_GET=300,
    LIMIT_USER_GET=900,
)
USER_BY_USERNAME = Endpoint(
    resource="/users/by/:username",
    regex=re.compile(r"/users/by/\w+"),
    LIMIT_APP_GET=300,
    LIMIT_USER_GET=900,
)
USERS_BY_USERNAME = Endpoint(
    resource="/users/by",
    regex=re.compile(r"/users/by"),
    LIMIT_APP_GET=300,
    LIMIT_USER_GET=900,
)
USER_FOLLOWING = Endpoint(
    resource="/users/:id/following",
    regex=re.compile(r"/users/\d+/following"),
    LIMIT_APP_GET=15,
    LIMIT_USER_GET=15,
    LIMIT_USER_POST=15,
)
USER_REMOVE_FOLLOWING = Endpoint(
    resource="/users/:id/following/:target_user_id",
    regex=re.compile(r"/users/\d+/following/\d+"),
    LIMIT_USER_DELETE=50,
)
USER_FOLLOWER = Endpoint(
    resource="/users/:id/followers",
    regex=re.compile(r"/users/\d+/followers"),
    LIMIT_APP_GET=15,
    LIMIT_USER_GET=15,
)
USER_BLOCKING = Endpoint(
    resource="/users/:id/blocking",
    regex=re.compile(r"/users/\d+/blocking"),
    LIMIT_USER_GET=15,
    LIMIT_USER_POST=50,
)
USER_REMOVE_BLOCKING = Endpoint(
    resource="/users/:id/blocking/:target_user_id",
    regex=re.compile(r"/users/\d+/blocking/\d+"),
    LIMIT_USER_DELETE=50,
)
USER_MUTING = Endpoint(
    resource="/users/:id/muting",
    regex=re.compile(r"/users/\d+/muting"),
    LIMIT_USER_GET=15,
    LIMIT_USER_POST=50,
)
USER_REMOVE_MUTING = Endpoint(
    resource="/users/:id/muting/:target_user_id",
    regex=re.compile(r"/users/\d+/muting/\d+"),
    LIMIT_USER_POST=50,
)

SPACE_BY_ID = Endpoint(
    resource="/spaces/:id",
    regex=re.compile(r"/spaces/\w+"),
    LIMIT_APP_GET=300,
)
SPACES_BY_IDS = Endpoint(
    resource="/spaces",
    regex=re.compile(r"/spaces"),
    LIMIT_APP_GET=300,
)
SPACES_BY_CREATORS = Endpoint(
    resource="/spaces/by/creator_ids",
    regex=re.compile(r"/spaces/by/creator_ids"),
    LIMIT_APP_GET=300,
)
SPACES_SEARCH = Endpoint(
    resource="/spaces/search",
    regex=re.compile("/spaces/search"),
    LIMIT_APP_GET=300,
)

LIST_BY_ID = Endpoint(
    resource="/lists/:id",
    regex=re.compile(r"/lists/\d+"),
    LIMIT_APP_GET=75,
    LIMIT_USER_GET=75,
)
LISTS_BY_USER = Endpoint(
    resource="/users/:id/owned_lists",
    regex=re.compile(r"/users/\d+/owned_lists"),
    LIMIT_APP_GET=15,
    LIMIT_USER_GET=15,
)
LISTS_MANAGE = Endpoint(
    resource="/lists",
    regex=re.compile(r"/lists"),
    LIMIT_USER_POST=300,
)
LISTS_MANAGE_BY_ID = Endpoint(
    resource="/lists/:id",
    regex=re.compile(r"/lists/\w+"),
    LIMIT_USER_PUT=300,
    LIMIT_USER_DELETE=300,
)
LIST_TWEETS = Endpoint(
    resource="/lists/:id/tweets",
    regex=re.compile(r"/lists/\d+/tweets"),
    LIMIT_APP_GET=900,
    LIMIT_USER_GET=900,
)
LIST_MEMBERS = Endpoint(
    resource="/lists/:id/members",
    regex=re.compile(r"/lists/\d+/members"),
    LIMIT_APP_GET=900,
    LIMIT_USER_GET=900,
)
LISTS_MEMBERSHIPS_BY_USER = Endpoint(
    resource="/users/:id/list_memberships",
    regex=re.compile(r"/users/\d+/list_memberships"),
    LIMIT_APP_GET=75,
    LIMIT_USER_GET=75,
)
LISTS_MANAGE_MEMBERS = Endpoint(
    resource="/lists/members",
    regex=re.compile(r"/lists/members"),
    LIMIT_USER_POST=300,
)
LISTS_MANAGE_MEMBERS_BY_ID = Endpoint(
    resource="/lists/:id/members/:user_id",
    regex=re.compile(r"/lists/\w+/members/\d+"),
    LIMIT_USER_DELETE=300,
)
LISTS_MANAGE_FOLLOWERS = Endpoint(
    resource="/lists/followers",
    regex=re.compile(r"/lists/followers"),
    LIMIT_USER_GET=180,
    LIMIT_APP_GET=180,
)
USER_FOLLOW_LISTS = Endpoint(
    resource="/users/:id/followed_lists",
    regex=re.compile(r"/users/\d+/followed_lists"),
    LIMIT_USER_POST=50,
    LIMIT_USER_GET=15,
    LIMIT_APP_GET=15,
)
USER_FOLLOW_LISTS_BY_ID = Endpoint(
    resource="/users/:id/followed_lists/:list_id",
    regex=re.compile(r"/users/\d+/followed_lists/\w+"),
    LIMIT_USER_DELETE=50,
)
USER_PINNED_LISTS = Endpoint(
    resource="/users/:id/pinned_lists",
    regex=re.compile(r"/users/\d+/pinned_lists"),
    LIMIT_USER_GET=15,
    LIMIT_USER_POST=50,
)
USER_PINNED_LISTS_BY_ID = Endpoint(
    resource="/users/:id/pinned_lists/:list_id",
    regex=re.compile(r"/users/\d+/pinned_lists/\w+"),
    LIMIT_USER_DELETE=50,
)

COMPLIANCE_JOB_BY_ID = Endpoint(
    resource="/compliance/jobs/:job_id",
    regex=re.compile(r"/compliance/jobs/\d+"),
    LIMIT_APP_GET=150,
)
COMPLIANCE_JOBS = Endpoint(
    resource="/compliance/jobs",
    regex=re.compile(r"/compliance/jobs"),
    LIMIT_APP_GET=150,
    LIMIT_APP_POST=150,
)
DM_EVENTS_BY_PARTICIPANT = Endpoint(
    resource="/dm_conversations/with/:participant_id/dm_events",
    regex=re.compile(r"/dm_conversations/with/\d+/dm_events"),
    LIMIT_APP_GET=300,
)
DM_EVENTS_BY_CONVERSATION = Endpoint(
    resource="/dm_conversations/:dm_conversation_id/dm_events",
    regex=re.compile(r"/dm_conversations/\d+/dm_events"),
    LIMIT_APP_GET=300,
)
DM_EVENTS = Endpoint(
    resource="/dm_events",
    regex=re.compile(r"/dm_events"),
    LIMIT_APP_GET=300,
)

DM_MESSAGE_TO_PARTICIPANT = Endpoint(
    resource="/dm_conversations/with/:participant_id/messages",
    regex=re.compile(r"/dm_conversations/with/\d+/messages"),
    LIMIT_APP_GET=200,
)
DM_MESSAGE_TO_CONVERSATION = Endpoint(
    resource="/dm_conversations/:dm_conversation_id/messages",
    regex=re.compile(r"/dm_conversations/\d+/messages"),
    LIMIT_APP_GET=200,
)
DM_CONVERSATIONS = Endpoint(
    resource="/dm_conversations",
    regex=re.compile(r"/dm_conversations"),
    LIMIT_APP_GET=200,
)

PATH_VAR_ENDPOINTS = [
    TWEET_BY_ID,
    TWEETS_BY_ID,
    USER_TIMELINE,
    USER_TIMELINE_REVERSE,
    USER_MENTIONS,
    TWEET_SEARCH_RECENT,
    TWEET_SEARCH_ALL,
    TWEET_COUNTS,
    TWEET_RETWEET_USER,
    TWEET_QUOTE_TWEETS,
    USER_TWEET_RETWEET,
    USER_TWEET_RETWEET_REMOVE,
    TWEET_LIKING_USER,
    USER_LIKED_TWEET,
    USER_TWEET_LIKE,
    USER_TWEET_LIKE_REMOVE,
    TWEET_HIDDEN,
    USER_BY_ID,
    USERS_BY_ID,
    USER_BY_USERNAME,
    USERS_BY_USERNAME,
    USER_FOLLOWING,
    USER_REMOVE_FOLLOWING,
    USER_FOLLOWER,
    USER_BLOCKING,
    USER_REMOVE_BLOCKING,
    USER_MUTING,
    USER_REMOVE_MUTING,
    SPACE_BY_ID,
    SPACES_BY_IDS,
    SPACES_BY_CREATORS,
    SPACES_SEARCH,
    LIST_BY_ID,
    LISTS_BY_USER,
    LISTS_MANAGE,
    LISTS_MANAGE_BY_ID,
    LIST_TWEETS,
    LIST_MEMBERS,
    LISTS_MEMBERSHIPS_BY_USER,
    LISTS_MANAGE_MEMBERS,
    LISTS_MANAGE_MEMBERS_BY_ID,
    LISTS_MANAGE_FOLLOWERS,
    USER_FOLLOW_LISTS,
    USER_FOLLOW_LISTS_BY_ID,
    USER_PINNED_LISTS,
    USER_PINNED_LISTS_BY_ID,
    COMPLIANCE_JOB_BY_ID,
    COMPLIANCE_JOBS,
    DM_EVENTS_BY_PARTICIPANT,
    DM_EVENTS_BY_CONVERSATION,
    DM_EVENTS,
    DM_MESSAGE_TO_PARTICIPANT,
    DM_MESSAGE_TO_CONVERSATION,
    DM_CONVERSATIONS,
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
        if auth_type.lower() not in ("user", "app"):
            raise PyTwitterError(f"Not support for auth type {auth_type}")
        self.auth_type = auth_type
        self.mapping = defaultdict(dict)

    @staticmethod
    def url_to_endpoint(url) -> Endpoint:
        resource = urlparse(url).path.replace("/2", "", 1)  # only replace api version
        for endpoint in PATH_VAR_ENDPOINTS:
            if re.fullmatch(endpoint.regex, resource):
                return endpoint
        return Endpoint(resource=resource)

    def set_limit(self, url, headers, method="GET") -> RateLimitData:
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
        :param method: request method
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
        self.mapping[endpoint.resource][method.upper()] = RateLimitData(**data)

        return self.get_limit(url=url, method=method)

    def get_limit(self, url, method="GET") -> RateLimitData:
        endpoint = self.url_to_endpoint(url=url)
        if method not in self.mapping.get(endpoint.resource, {}):
            limit = endpoint.get_limit(auth_type=self.auth_type, method=method)
            return RateLimitData(limit=limit, remaining=limit)
        return self.mapping[endpoint.resource][method.upper()]
