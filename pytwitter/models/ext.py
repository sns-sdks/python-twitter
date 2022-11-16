"""
    extends objects

    Refer: https://developer.twitter.com/en/docs/twitter-api/expansions
"""
from dataclasses import dataclass, field
from typing import List, Optional, Union

from . import (
    BaseModel,
    Media,
    Place,
    Poll,
    Tweet,
    User,
    Space,
    Topic,
    DirectMessageEvent,
    ComplianceJob,
    StreamRule,
    TwitterList,
)


@dataclass
class Error(BaseModel):
    """
    A class representing the error object for request.
    """

    detail: Optional[str] = field(default=None)
    title: Optional[str] = field(default=None)
    resource_type: Optional[str] = field(default=None, repr=False)
    parameter: Optional[str] = field(default=None, repr=False)
    value: Optional[str] = field(default=None, repr=False)
    type: Optional[str] = field(default=None, repr=False)


@dataclass
class MetaSummary(BaseModel):
    """
    A class representing the meta summary object for request.
    Now works for stream rules api.
    """

    created: Optional[int] = field(default=None)
    not_created: Optional[int] = field(default=None, repr=False)
    valid: Optional[int] = field(default=None)
    invalid: Optional[int] = field(default=None, repr=False)
    deleted: Optional[int] = field(default=None)
    not_deleted: Optional[int] = field(default=None, repr=False)


@dataclass
class Meta(BaseModel):
    """
    A class representing the meta object for request.
    """

    result_count: Optional[int] = field(default=None)
    previous_token: Optional[str] = field(default=None, repr=False)
    next_token: Optional[str] = field(default=None, repr=False)
    oldest_id: Optional[str] = field(default=None, repr=False)
    newest_id: Optional[str] = field(default=None, repr=False)
    sent: Optional[str] = field(default=None, repr=False)
    summary: Optional[MetaSummary] = field(default=None, repr=False)
    total_tweet_count: Optional[int] = field(default=None, repr=False)


@dataclass
class Includes(BaseModel):
    """
    A class representing the expansions object for main request thread.
    """

    media: Optional[List[Media]] = field(default=None, compare=False)
    places: Optional[List[Place]] = field(default=None, compare=False)
    polls: Optional[List[Poll]] = field(default=None, compare=False)
    tweets: Optional[List[Tweet]] = field(default=None, compare=False)
    users: Optional[List[User]] = field(default=None, compare=False)
    topics: Optional[List[Topic]] = field(default=None, compare=False)


@dataclass
class TweetCount(BaseModel):
    """
    A class representing the counts for tweets match a search query.
    Refer: https://developer.twitter.com/en/docs/twitter-api/tweets/counts/api-reference/get-tweets-counts-recent
    """

    start: Optional[str] = field(default=None)
    end: Optional[str] = field(default=None)
    tweet_count: Optional[int] = field(default=None)


@dataclass
class Response:
    """
    A class representing for the twitter response.
    """

    data: Optional[
        Union[
            User,
            Tweet,
            Media,
            Poll,
            Place,
            Space,
            ComplianceJob,
            TwitterList,
            DirectMessageEvent,
            List[User],
            List[Tweet],
            List[Media],
            List[Poll],
            List[Place],
            List[StreamRule],
            List[TweetCount],
            List[TwitterList],
            List[Space],
            List[ComplianceJob],
            List[DirectMessageEvent],
        ]
    ]
    includes: Optional[Includes] = field(default=None, repr=False)
    meta: Optional[Meta] = field(default=None, repr=False)
    errors: Optional[List[Error]] = field(default=None, repr=False)
